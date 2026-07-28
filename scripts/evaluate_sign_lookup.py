"""
Evaluates sign lookup the same way the ASL Citizen paper evaluates its own
dictionary-retrieval task: given a held-out test video, is the correct sign
among the top-k retrieved matches? Reports recall@1, @5, and @10.

Needs a reference database built by scripts/build_sign_reference.py from the
TRAIN split, and a separate set of test videos + labels (e.g. ASL Citizen's
splits/test.csv) that weren't used to build the reference — otherwise this
measures memorization, not retrieval.

Usage:
    python scripts/evaluate_sign_lookup.py \\
        --reference sign_reference.npz \\
        --videos-dir ASL_Citizen/videos \\
        --labels-csv ASL_Citizen/splits/test.csv
"""

import argparse
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.sign_lookup import extract_landmark_sequence_from_video, sequence_to_feature, top_k_matches


def load_reference(path: str) -> dict:
    data = np.load(path)
    reference = {}
    for key in data.files:
        if key.startswith("label::"):
            label = key[len("label::"):]
            reference[label] = list(data[key])
    return reference


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--reference", required=True)
    parser.add_argument("--videos-dir", required=True)
    parser.add_argument("--labels-csv", required=True)
    parser.add_argument("--video-col", default="Video file")
    parser.add_argument("--label-col", default="Gloss")
    parser.add_argument("--max-test-clips", type=int, default=200)
    args = parser.parse_args()

    reference = load_reference(args.reference)
    if not reference:
        raise SystemExit(f"No classes found in {args.reference} — did build_sign_reference.py run successfully?")
    known_labels = set(reference.keys())
    print(f"Reference covers {len(known_labels)} classes.")

    with open(args.labels_csv, newline="") as f:
        rows = list(csv.DictReader(f))

    ranks = []  # 1-indexed position of the correct label in the ranking, or None if not found in top-k
    evaluated = 0
    for row in rows:
        label = row[args.label_col]
        if label not in known_labels:
            continue  # only evaluate on classes we actually have a reference for
        if evaluated >= args.max_test_clips:
            break

        video_path = os.path.join(args.videos_dir, row[args.video_col])
        if not os.path.exists(video_path):
            continue

        seq = extract_landmark_sequence_from_video(video_path)
        if seq.shape[0] == 0:
            continue

        query_feature = sequence_to_feature(seq)
        ranked = top_k_matches(query_feature, reference, k=len(reference))
        rank_labels = [r[0] for r in ranked]
        rank = rank_labels.index(label) + 1 if label in rank_labels else None
        ranks.append(rank)
        evaluated += 1
        print(f"  {row[args.video_col]} (true: {label}) -> rank {rank}")

    if not ranks:
        raise SystemExit("No test clips evaluated — check paths and column names.")

    def recall_at(k):
        return sum(1 for r in ranks if r is not None and r <= k) / len(ranks)

    print(f"\nEvaluated {len(ranks)} test clips.")
    print(f"Recall@1:  {recall_at(1):.1%}")
    print(f"Recall@5:  {recall_at(5):.1%}")
    print(f"Recall@10: {recall_at(10):.1%}")


if __name__ == "__main__":
    main()
