"""
Evaluates the built-in MediaPipe gesture recognizer against a labeled set of
hand-gesture photos, and writes a markdown report with per-class precision,
recall, F1, a confusion matrix, false-activation rate, and inference latency.

Expected folder layout (one folder per class, any number of .jpg/.jpeg/.png
images per folder):

    test_data/gestures/
        Thumb_Up/*.jpg
        Thumb_Down/*.jpg
        Victory/*.jpg
        Pointing_Up/*.jpg
        Fist/*.jpg
        Open_Palm/*.jpg
        ILoveYou/*.jpg
        None/*.jpg          # photos with no hand, or a hand making a gesture
                             # the model doesn't support — used to measure
                             # the false-activation rate: how often the model
                             # confidently reports a gesture when it shouldn't

You don't need every class populated to get useful numbers — this evaluates
whatever classes have images in them.

Usage:
    python scripts/evaluate_gestures.py test_data/gestures
    python scripts/evaluate_gestures.py test_data/gestures --report my_report.md
"""

import argparse
import os
import sys
import time

import mediapipe as mp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.gesture_capture import MODEL_PATH  # reuse the same model the app uses

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Folder name (matches the app's GESTURE_LABELS naming) -> the label MediaPipe
# itself actually returns. Only "Fist" differs (MediaPipe calls it Closed_Fist).
FOLDER_TO_MODEL_LABEL = {
    "Thumb_Up": "Thumb_Up",
    "Thumb_Down": "Thumb_Down",
    "Victory": "Victory",
    "Pointing_Up": "Pointing_Up",
    "Fist": "Closed_Fist",
    "Open_Palm": "Open_Palm",
    "ILoveYou": "ILoveYou",
}

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def load_recognizer() -> "GestureRecognizer":
    if not os.path.exists(MODEL_PATH):
        raise SystemExit(f"Model file not found at {MODEL_PATH}")
    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.IMAGE,
    )
    return GestureRecognizer.create_from_options(options)


def predict_one(recognizer, image_path: str):
    """Returns (predicted_label_or_None, confidence, latency_seconds)."""
    image = mp.Image.create_from_file(image_path)
    start = time.time()
    result = recognizer.recognize(image)
    latency = time.time() - start
    if not result.gestures or not result.gestures[0]:
        return None, 0.0, latency
    top = result.gestures[0][0]
    return top.category_name, top.score, latency


def collect_predictions(test_dir: str):
    recognizer = load_recognizer()
    class_dirs = sorted(
        d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))
    )
    if not class_dirs:
        raise SystemExit(f"No class folders found under {test_dir}")

    y_true, y_pred, latencies, per_image = [], [], [], []

    for folder_label in class_dirs:
        expected = None if folder_label == "None" else FOLDER_TO_MODEL_LABEL.get(
            folder_label, folder_label
        )
        folder_path = os.path.join(test_dir, folder_label)
        images = sorted(
            f for f in os.listdir(folder_path) if f.lower().endswith(IMAGE_EXTENSIONS)
        )
        if not images:
            print(f"  (skipping {folder_label}/ — no images found)")
            continue

        for fname in images:
            path = os.path.join(folder_path, fname)
            pred, score, latency = predict_one(recognizer, path)
            latencies.append(latency)
            y_true.append(expected or "None")
            y_pred.append(pred or "None")
            per_image.append(
                {
                    "file": f"{folder_label}/{fname}",
                    "expected": expected or "None",
                    "predicted": pred or "None",
                    "confidence": round(score, 3),
                }
            )

    return y_true, y_pred, latencies, per_image


def compute_per_class_metrics(y_true, y_pred, labels):
    metrics = {}
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        support = tp + fn
        metrics[label] = {"precision": precision, "recall": recall, "f1": f1, "support": support}
    return metrics


def compute_confusion_matrix(y_true, y_pred, labels):
    idx = {label: i for i, label in enumerate(labels)}
    matrix = [[0] * len(labels) for _ in labels]
    for t, p in zip(y_true, y_pred):
        matrix[idx[t]][idx[p]] += 1
    return matrix


def render_report(y_true, y_pred, latencies, per_image, test_dir) -> str:
    labels = sorted(set(y_true) | set(y_pred))
    metrics = compute_per_class_metrics(y_true, y_pred, labels)
    matrix = compute_confusion_matrix(y_true, y_pred, labels)

    real_classes = [l for l in labels if l != "None"]
    macro_f1 = (
        sum(metrics[l]["f1"] for l in real_classes) / len(real_classes)
        if real_classes
        else 0.0
    )
    none_total = sum(1 for t in y_true if t == "None")
    none_false_activations = sum(1 for t, p in zip(y_true, y_pred) if t == "None" and p != "None")
    false_activation_rate = (none_false_activations / none_total) if none_total else None
    avg_latency_ms = (sum(latencies) / len(latencies) * 1000) if latencies else 0.0

    lines = []
    lines.append("# Gesture Recognizer Evaluation Report\n")
    lines.append(f"Test set: `{test_dir}`  \nTotal images evaluated: **{len(y_true)}**\n")

    lines.append("## Per-class metrics\n")
    lines.append("| Class | Precision | Recall | F1 | Support |")
    lines.append("|---|---|---|---|---|")
    for label in labels:
        m = metrics[label]
        lines.append(
            f"| {label} | {m['precision']:.2f} | {m['recall']:.2f} | {m['f1']:.2f} | {m['support']} |"
        )
    lines.append(f"\n**Macro F1 (excluding None class): {macro_f1:.3f}**\n")

    if false_activation_rate is not None:
        lines.append(
            f"**False-activation rate** (no-hand/unsupported-gesture images incorrectly "
            f"reported as a real gesture): {false_activation_rate:.1%} "
            f"({none_false_activations}/{none_total})\n"
        )
    else:
        lines.append(
            "**False-activation rate**: not measured — add photos to a `None/` folder "
            "(no hand, or an unsupported gesture) to measure this.\n"
        )

    lines.append(f"**Average inference latency**: {avg_latency_ms:.1f} ms/image\n")

    lines.append("## Confusion matrix\n")
    lines.append("Rows = actual class, columns = predicted class.\n")
    header = "| actual \\\\ predicted | " + " | ".join(labels) + " |"
    lines.append(header)
    lines.append("|" + "---|" * (len(labels) + 1))
    for i, label in enumerate(labels):
        row = " | ".join(str(v) for v in matrix[i])
        lines.append(f"| **{label}** | {row} |")

    lines.append("\n## Per-image predictions\n")
    lines.append("| File | Expected | Predicted | Confidence |")
    lines.append("|---|---|---|---|")
    for r in per_image:
        flag = "" if r["expected"] == r["predicted"] else " ⚠️"
        lines.append(
            f"| {r['file']} | {r['expected']} | {r['predicted']}{flag} | {r['confidence']} |"
        )

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("test_dir", help="Path to labeled gesture image folders")
    parser.add_argument(
        "--report", default="gesture_eval_report.md", help="Output markdown report path"
    )
    args = parser.parse_args()

    print(f"Evaluating gesture recognizer against {args.test_dir} ...")
    y_true, y_pred, latencies, per_image = collect_predictions(args.test_dir)

    if not y_true:
        raise SystemExit("No images found to evaluate. Check your folder structure.")

    report = render_report(y_true, y_pred, latencies, per_image, args.test_dir)
    with open(args.report, "w") as f:
        f.write(report)

    print(f"Evaluated {len(y_true)} images. Report written to {args.report}")


if __name__ == "__main__":
    main()
