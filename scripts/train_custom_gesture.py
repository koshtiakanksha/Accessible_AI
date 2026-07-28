"""
Trains a CUSTOM gesture recognizer on your own gesture photos, using
MediaPipe Model Maker, and exports a new .task model file you can drop in to
replace gesture_recognizer.task.

This is a template following Google's documented Model Maker API — it is NOT
runnable as-is, because it needs two things this repo doesn't have:
  1. `mediapipe-model-maker` installed (a heavy, TensorFlow-based package,
     separate from the lightweight `mediapipe` runtime the app itself uses)
  2. Your own labeled dataset of gesture photos — Model Maker only retrains
     the final gesture-classification step on top of MediaPipe's existing
     hand-landmark detector, but that still means dozens of real photos per
     new gesture, from you or whoever's contributing the gesture.

WHY THIS IS A SEPARATE, BIGGER PROJECT THAN ADDING SIGN VOCABULARY:
The 7 gestures in Gesture Shortcuts (Thumb_Up, Thumb_Down, Victory,
Pointing_Up, Fist, Open_Palm, ILoveYou) are the fixed built-in output classes
of Google's pretrained model bundle. There's no config flag or file you can
add to make it recognize an 8th gesture — the classifier genuinely doesn't
have an output for anything else. Getting a new gesture requires collecting
example data and training a new classification head, which is what this
script does.

Expected dataset layout (photos, not video — one folder per gesture):

    gesture_training_data/
        thumbs_up/*.jpg          # existing gestures can be included too,
        peace_sign/*.jpg         # to keep recognizing them alongside new ones
        wave/*.jpg                <- a brand new gesture, e.g.
        stop_hand/*.jpg           <- another new one
        none/*.jpg                <- REQUIRED: photos with no hand, or a hand
                                      not making any supported gesture

Rule of thumb from Google's own tutorials: aim for at least ~100 images per
class, varied in lighting, background, and hand position/rotation — a
handful of photos will train a model that overfits and doesn't generalize.

Usage (once you have mediapipe-model-maker installed and a real dataset):
    pip install mediapipe-model-maker
    python scripts/train_custom_gesture.py gesture_training_data --export-dir exported_model
    # then copy exported_model/gesture_recognizer.task over the app's
    # gesture_recognizer.task, and update lib/gesture_capture.py's
    # GESTURE_LABELS to match your new class names.
"""

import argparse


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("dataset_dir", help="Folder of gesture_name/*.jpg subfolders (see docstring)")
    parser.add_argument("--export-dir", default="exported_model")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    args = parser.parse_args()

    try:
        from mediapipe_model_maker import gesture_recognizer
    except ImportError:
        raise SystemExit(
            "mediapipe-model-maker isn't installed. This is a separate, heavier "
            "package from the `mediapipe` runtime the app uses — run:\n"
            "    pip install mediapipe-model-maker\n"
            "before running this script."
        )

    print(f"Loading dataset from {args.dataset_dir} ...")
    data = gesture_recognizer.Dataset.from_folder(
        dirname=args.dataset_dir,
        hparams=gesture_recognizer.HandDataPreprocessingParams(),
    )
    # Images where MediaPipe's hand detector doesn't find a hand at all are
    # silently dropped by from_folder — if your resulting dataset size looks
    # much smaller than the number of photos you added, that's usually why:
    # check lighting/framing on the dropped photos.

    train_data, rest_data = data.split(0.8)
    validation_data, test_data = rest_data.split(0.5)
    print(
        f"Split into {train_data.size} train / {validation_data.size} validation / "
        f"{test_data.size} test examples."
    )

    hparams = gesture_recognizer.HParams(
        export_dir=args.export_dir,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
    )
    options = gesture_recognizer.GestureRecognizerOptions(hparams=hparams)

    print("Training...")
    model = gesture_recognizer.GestureRecognizer.create(
        train_data=train_data, validation_data=validation_data, options=options
    )

    loss, accuracy = model.evaluate(test_data)
    print(f"Test loss: {loss:.4f}, test accuracy: {accuracy:.4f}")

    model.export_model()
    print(
        f"\nExported to {args.export_dir}/gesture_recognizer.task — copy this over the "
        f"app's gesture_recognizer.task, and update GESTURE_LABELS in "
        f"lib/gesture_capture.py to match your class names."
    )


if __name__ == "__main__":
    main()
