#!/usr/bin/env python3
"""
Optimize blog cover images into responsive derivatives.

Drop a source cover into /images named  cover-<post-slug>.(jpg|png)  — any
size (AI-generated covers are often large). This builds, for each source:
  - WebP at widths 480 / 800 / 1200 (capped at the source width)
  - a JPEG fallback at min(1200, native width)

Outputs are git-ignored and rebuilt at deploy time, so the repo only carries
the source covers + this script.

Local preview:   python3 scripts/build-images.py
Requires:        Pillow  (pip install Pillow)
"""
import os, re, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "images")
WIDTHS = [480, 800, 1200]
WEBP_QUALITY = 82
JPG_QUALITY = 82

DERIVATIVE = re.compile(r"-\d+\.(webp|jpg)$", re.IGNORECASE)


def is_source(path):
    return not DERIVATIVE.search(os.path.basename(path))


def process(src):
    name = os.path.splitext(os.path.basename(src))[0]
    im = Image.open(src).convert("RGB")
    ow, oh = im.size
    made = 0

    for w in WIDTHS:
        if w > ow:
            continue
        h = round(oh * w / ow)
        im.resize((w, h), Image.LANCZOS).save(
            os.path.join(IMG_DIR, f"{name}-{w}.webp"), "WEBP",
            quality=WEBP_QUALITY, method=6)
        made += 1

    fw = min(1200, ow)
    fh = round(oh * fw / ow)
    fallback = im.resize((fw, fh), Image.LANCZOS)
    fallback.save(os.path.join(IMG_DIR, f"{name}-{fw}.jpg"), "JPEG",
                  quality=JPG_QUALITY, optimize=True, progressive=True)
    made += 1
    if fw not in WIDTHS:
        fallback.save(os.path.join(IMG_DIR, f"{name}-{fw}.webp"), "WEBP",
                      quality=WEBP_QUALITY, method=6)
        made += 1

    print(f"  {os.path.basename(src):28} {ow}x{oh}  -> {made} files")
    return made


def main():
    if not os.path.isdir(IMG_DIR):
        print("No /images directory")
        return
    sources = [p for p in glob.glob(os.path.join(IMG_DIR, "*.jpg"))
               + glob.glob(os.path.join(IMG_DIR, "*.png")) if is_source(p)]
    if not sources:
        print("No source cover images found in /images")
        return
    print(f"Optimizing {len(sources)} cover(s):")
    total = sum(process(p) for p in sorted(sources))
    print(f"Done — {total} responsive files generated.")


if __name__ == "__main__":
    main()
