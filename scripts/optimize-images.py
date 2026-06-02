#!/usr/bin/env python3
"""Optimize images/ for web distribution by converting rasters to WebP.

- Longest edge clamped to MAX_EDGE (no upscaling).
- Photos -> lossy WebP (QUALITY); images with alpha -> lossless/alpha WebP.
- SVG is vector and left untouched.
- Originals are removed once a .webp replacement is written (recoverable via git).

Prints a before/after size report and a JSON rename map (old basename -> new
basename) so references can be rewritten.
"""

import json
import sys
from pathlib import Path

from PIL import Image

IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"
MAX_EDGE = 2000
QUALITY = 80
RASTER_EXTS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".webp"}
SKIP_EXTS = {".svg"}


def main():
    if not IMAGES_DIR.is_dir():
        sys.exit(f"images dir not found: {IMAGES_DIR}")

    rename_map = {}
    before_total = 0
    after_total = 0
    converted = 0

    for path in sorted(IMAGES_DIR.iterdir()):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in SKIP_EXTS:
            continue
        if ext not in RASTER_EXTS:
            print(f"  skip (unknown ext): {path.name}")
            continue

        before = path.stat().st_size
        before_total += before

        with Image.open(path) as im:
            im.load()
            has_alpha = im.mode in ("RGBA", "LA") or (
                im.mode == "P" and "transparency" in im.info
            )
            # Only keep lossless/alpha if the alpha channel is actually used;
            # a fully-opaque alpha channel just bloats the file.
            if has_alpha:
                alpha = im.convert("RGBA").getchannel("A")
                lo, _ = alpha.getextrema()
                has_alpha = lo < 255

            # Downscale longest edge, never upscale.
            w, h = im.size
            scale = min(1.0, MAX_EDGE / max(w, h))
            if scale < 1.0:
                im = im.resize(
                    (round(w * scale), round(h * scale)), Image.LANCZOS
                )

            out_path = path.with_suffix(".webp")
            if has_alpha:
                im = im.convert("RGBA")
                im.save(out_path, "WEBP", lossless=True, method=6)
            else:
                im = im.convert("RGB")
                im.save(out_path, "WEBP", quality=QUALITY, method=6)

        after = out_path.stat().st_size
        after_total += after
        converted += 1

        # Remove the original if it was a different file (jpg/png/tiff -> webp).
        if path.suffix.lower() != ".webp":
            rename_map[path.name] = out_path.name
            path.unlink()

        pct = (1 - after / before) * 100 if before else 0
        alpha = " [alpha]" if has_alpha else ""
        print(
            f"  {path.name:55s} {before/1e6:6.2f}MB -> "
            f"{after/1e6:5.2f}MB ({pct:5.1f}% smaller){alpha}"
        )

    print()
    print(f"Converted {converted} images")
    print(
        f"Total: {before_total/1e6:.1f}MB -> {after_total/1e6:.1f}MB "
        f"({(1 - after_total/before_total)*100:.1f}% smaller)"
    )

    map_path = IMAGES_DIR.parent / "scripts" / "rename-map.json"
    map_path.write_text(json.dumps(rename_map, indent=2))
    print(f"Rename map written to {map_path}")


if __name__ == "__main__":
    main()
