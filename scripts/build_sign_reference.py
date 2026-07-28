"""
Builds the reference database that pages/6_ASL Sign Lookup.py and
scripts/evaluate_sign_lookup.py compare against: for each chosen sign class,
extracts a landmark-sequence feature vector from each of its example videos.

This needs the ASL Citizen dataset downloaded locally first — that's a
deliberate line this script doesn't cross for you:

    wget https://download.microsoft.com/download/b/8/8/b88c0bae-e6c1-43e1-8726-98cf5af36ca4/ASL_Citizen.zip
    unzip ASL_Citizen.zip

See https://www.microsoft.com/en-us/research/project/asl-citizen/ for the
license (non-commercial research use) and citation requirement. ASL Citizen
ships a CSV (splits/train.csv etc.) with columns including at least a video
filename and a gloss/label — check the actual column names in the version
you download, since dataset releases sometimes rename these.

Expected local layout after extraction (adjust --videos-dir / --labels-csv if
yours differs):

    ASL_Citizen/
        videos/*.mp4
        splits/train.csv   # columns: Video file, Gloss (or similar)

Usage:
    python scripts/build_sign_reference.py \\
        --videos-dir ASL_Citizen/videos \\
        --labels-csv ASL_Citizen/splits/train.csv \\
        --classes hello thank-you please yes no help water bathroom \\
        --out sign_reference.npz

Start with a small --classes list (10-30 signs relevant to your app, e.g.
greetings and everyday needs) rather than all 2,731 — this script processes
every matching video through the gesture recognizer, which takes real time
per video, and a smaller, well-chosen vocabulary is more useful for a working
demo than a huge one that takes a day to build and is still incomplete.
"""

import argparse
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.sign_lookup import extract_landmark_sequence_from_video, sequence_to_feature


def load_labels(csv_path: str, video_col: str, label_col: str):
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        if video_col not in reader.fieldnames or label_col not in reader.fieldnames:
            raise SystemExit(
                f"Columns {video_col!r}/{label_col!r} not found in {csv_path}. "
                f"Actual columns: {reader.fieldnames}. Pass --video-col/--label-col "
                f"to match your CSV."
            )
        for row in reader:
            rows.append((row[video_col], row[label_col]))
    return rows


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--videos-dir", required=True)
    parser.add_argument("--labels-csv", required=True)
    parser.add_argument("--video-col", default="Video file")
    parser.add_argument("--label-col", default="Gloss")
    parser.add_argument("--classes", nargs="+", required=True, help="Sign labels to include")
    parser.add_argument("--max-per-class", type=int, default=20)
    parser.add_argument("--out", default="sign_reference.npz")
    args = parser.parse_args()

    rows = load_labels(args.labels_csv, args.video_col, args.label_col)
    wanted = set(args.classes)

    features_by_label = {label: [] for label in wanted}
    counts = {label: 0 for label in wanted}

    for video_file, label in rows:
        if label not in wanted or counts[label] >= args.max_per_class:
            continue
        video_path = os.path.join(args.videos_dir, video_file)
        if not os.path.exists(video_path):
            print(f"  (skipping missing file: {video_path})")
            continue

        seq = extract_landmark_sequence_from_video(video_path)
        if seq.shape[0] == 0:
            print(f"  (no hand detected in {video_file}, skipping)")
            continue

        features_by_label[label].append(sequence_to_feature(seq))
        counts[label] += 1
        print(f"  processed {video_file} -> {label} ({counts[label]}/{args.max_per_class})")

    empty_classes = [label for label, feats in features_by_label.items() if not feats]
    if empty_classes:
        print(f"\nWARNING: no usable videos found for: {', '.join(empty_classes)}")
        print("Check --video-col/--label-col match your CSV, and that label spelling matches exactly.")

    np.savez(
        args.out,
        **{
            f"label::{label}": np.array(feats)
            for label, feats in features_by_label.items()
            if feats
        },
    )
    total = sum(len(f) for f in features_by_label.values())
    print(f"\nWrote {args.out}: {total} example clips across {len(features_by_label) - len(empty_classes)} classes.")


if __name__ == "__main__":
    main()
