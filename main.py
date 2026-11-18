#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261117 (Python 3.13, stdlib only).

Copies the entry image held in this repository to /output/entry.png
(or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader). The copy is
byte-for-byte, so both graded runs write identical output. No network,
no randomness, no timestamps.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
