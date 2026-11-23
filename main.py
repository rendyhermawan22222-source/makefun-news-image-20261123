"""make.fun news-image-20261123 entry: writes the front page to /output/entry.png.

The page was composed ahead of time by build/compose.py and committed as
entry.png. This program only copies those bytes, so every run produces
byte-identical output and needs no network.
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
TARGET_DIR = "/output"
TARGET = os.path.join(TARGET_DIR, "entry.png")
SHA256 = "acc0531a5140af600da6056f113480703b497cad724a86e6169bc2e670e57ebe"


def main() -> None:
    with open(SOURCE, "rb") as f:
        if hashlib.sha256(f.read()).hexdigest() != SHA256:
            raise SystemExit("entry.png does not match the committed front page")
    os.makedirs(TARGET_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)


if __name__ == "__main__":
    main()
