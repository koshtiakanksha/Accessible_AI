"""
Checks sign_language_images/manifest.json against what's actually on disk:
- every manifest entry's image file exists
- every image file on disk has a manifest entry (nothing orphaned/unused)
- no duplicate phrases

Usage:
    python scripts/validate_sign_vocabulary.py
"""

import json
import os
import sys

FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sign_language_images")
MANIFEST_PATH = os.path.join(FOLDER, "manifest.json")
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")


def find_problems(manifest: list, folder: str) -> list:
    """Core check, separated from path resolution and I/O so it's directly
    unit-testable against a temporary folder instead of the real one."""
    problems = []
    seen_phrases = set()
    referenced_images = set()

    for entry in manifest:
        phrase = entry.get("phrase")
        image = entry.get("image")
        if not phrase or not image:
            problems.append(f"Entry missing 'phrase' or 'image': {entry}")
            continue
        if phrase.lower() in seen_phrases:
            problems.append(f"Duplicate phrase in manifest: '{phrase}'")
        seen_phrases.add(phrase.lower())

        referenced_images.add(image)
        if not os.path.exists(os.path.join(folder, image)):
            problems.append(f"Manifest entry '{phrase}' points to missing file: {image}")

    on_disk = {f for f in os.listdir(folder) if f.lower().endswith(IMAGE_EXTENSIONS)}
    orphaned = on_disk - referenced_images
    for f in sorted(orphaned):
        problems.append(f"Image file has no manifest entry (unused): {f}")

    return problems


def main():
    if not os.path.exists(MANIFEST_PATH):
        sys.exit(f"No manifest found at {MANIFEST_PATH}")

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    problems = find_problems(manifest, FOLDER)
    on_disk_count = len([f for f in os.listdir(FOLDER) if f.lower().endswith(IMAGE_EXTENSIONS)])

    print(f"Checked {len(manifest)} manifest entries against {on_disk_count} image files.")
    if problems:
        print(f"\n{len(problems)} problem(s) found:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("Everything matches up.")


if __name__ == "__main__":
    main()
