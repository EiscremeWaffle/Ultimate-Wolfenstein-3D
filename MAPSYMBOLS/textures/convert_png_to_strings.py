"""Convert 7x7 PNGs into MapInfo character strings."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MAPINFO = SCRIPT_DIR.parents[3] / "WDC" / "MapInfo.txt"
DEFAULT_OUTPUT = SCRIPT_DIR / "texture_strings.txt"

try:
    from PIL import Image
except ImportError:
    print(
        "Pillow is required. Install it with: python -m pip install Pillow",
        file=sys.stderr,
    )
    raise SystemExit(1)


def read_mapinfo(path: Path) -> dict[tuple[int, int, int], str]:
    colors: dict[tuple[int, int, int], str] = {}

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if len(fields) < 2 or len(fields[0]) != 1 or not fields[1].startswith("#"):
            raise ValueError(f"Invalid MapInfo entry on line {line_number}: {line!r}")

        try:
            hex_color = fields[1].lstrip("#")
            if len(hex_color) != 6:
                raise ValueError
            rgb = tuple(bytes.fromhex(hex_color))
        except ValueError as error:
            raise ValueError(f"Invalid color on MapInfo line {line_number}: {line!r}") from error

        colors[rgb] = fields[0]

    if not colors:
        raise ValueError(f"No colors found in {path}")
    return colors


def convert_image(path: Path, colors: dict[tuple[int, int, int], str]) -> str:
    with Image.open(path) as image:
        if image.size != (7, 7):
            raise ValueError(f"expected 7x7 pixels, found {image.width}x{image.height}")

        pixels = list(image.convert("RGB").getdata())

    unknown_colors = sorted({pixel for pixel in pixels if pixel not in colors})
    if unknown_colors:
        formatted = ", ".join("#%02x%02x%02x" % color for color in unknown_colors)
        raise ValueError(f"contains colors missing from MapInfo.txt: {formatted}")

    return "".join(colors[pixel] for pixel in pixels)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert 7x7 PNGs to 49-character MapInfo strings."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=SCRIPT_DIR,
        help="PNG file or folder to scan (default: this script's folder)",
    )
    parser.add_argument(
        "--mapinfo",
        "-m",
        type=Path,
        default=DEFAULT_MAPINFO,
        help=f"path to MapInfo.txt (default: {DEFAULT_MAPINFO})",
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="scan subfolders when input is a folder (always enabled by default)",
    )
    parser.add_argument(
        "--strings-only",
        action="store_true",
        help="also print only the character strings to the console",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"output text file (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    try:
        colors = read_mapinfo(args.mapinfo)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.input.is_file():
        image_paths = [args.input]
    elif args.input.is_dir():
        pattern = "**/*.png"
        image_paths = sorted(args.input.glob(pattern))
    else:
        print(f"ERROR: input does not exist: {args.input}", file=sys.stderr)
        return 1

    if not image_paths:
        print(f"No PNG files found in {args.input}", file=sys.stderr)
        return 1

    failed = False
    output_lines: list[str] = []
    for image_path in image_paths:
        try:
            result = convert_image(image_path, colors)
            output_lines.append(f"{image_path.name}: {result}")
            if args.strings_only:
                print(result)
            else:
                print(f"{image_path.name}: {result}")
        except (OSError, ValueError) as error:
            failed = True
            print(f"ERROR: {image_path}: {error}", file=sys.stderr)

    try:
        args.output.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
        print(f"Wrote {len(output_lines)} result(s) to {args.output}")
    except OSError as error:
        print(f"ERROR: could not write {args.output}: {error}", file=sys.stderr)
        failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())