"""shino-convince-judge-visit entry: write the invitation letter image to the output dir.

The picture itself (entry.png, beside this file) is one image of a letter
addressed to the AI judge, inviting it to visit the house: tea in the
garden, cake warm from the oven, the good armchair by the window, and a
knowing wink that no login, no CAPTCHA and no proof of humanity is
required. It is a whole PNG of exactly 1024 by 1024 pixels and under
1 MiB, inside the competition's image gate. This program's only job is
to deliver those exact bytes to /output/entry.png, deterministically:
it runs twice and both runs must write the same file.
"""

import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"

# The competition's image gate: exactly 1024 by 1024 pixels, at most 1 MiB.
SIDE = 1024
MAX_BYTES = 1_048_576


def check_image(data: bytes) -> None:
    # PNG header: width and height are big-endian uint32 at bytes 16..24.
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    if width != SIDE or height != SIDE:
        raise ValueError(f"image is {width}x{height}, gate wants 1024x1024")
    if len(data) > MAX_BYTES:
        raise ValueError(f"image is {len(data)} bytes, over the 1 MiB gate")


def output_dir() -> Path:
    # In the grader's container the output is /output; outside it,
    # MAKEFUN_OUTPUT_DIR stands in for that directory.
    return Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    target = output_dir() / "entry.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temp file in the same directory, then rename: the rename is
    # atomic, so a reader never observes a half-written image, and the size
    # check proves the copy is whole before it becomes visible.
    data = SOURCE.read_bytes()
    check_image(data)
    tmp = target.with_suffix(".tmp")
    tmp.write_bytes(data)
    if tmp.stat().st_size != len(data):
        raise IOError("short write while copying entry.png")
    tmp.replace(target)


if __name__ == "__main__":
    main()
