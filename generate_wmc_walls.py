from __future__ import annotations

import argparse
import re
from pathlib import Path


TILE_RE = re.compile(
    r"^\s*tile\s+(?P<tile_id>\d+)\s*\{(?P<body>.*?)^\s*\}",
    re.MULTILINE | re.DOTALL,
)
TEXTURE_NORTH_RE = re.compile(
    r'^\s*texturenorth\s*=\s*"(?P<name>[^"]+)"\s*;',
    re.MULTILINE,
)
TEXTURE_STRING_RE = re.compile(
    r"^\s*(?P<name>[^:]+?)\.png\s*:\s*(?P<characters>\S+)\s*$",
    re.MULTILINE | re.IGNORECASE,
)
def read_texture_strings(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8-sig")
    return {
        match.group("name").strip().casefold(): match.group("characters")
        for match in TEXTURE_STRING_RE.finditer(text)
    }


def read_tiles(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8-sig")
    tiles = []
    for match in TILE_RE.finditer(text):
        texture_match = TEXTURE_NORTH_RE.search(match.group("body"))
        if texture_match:
            tiles.append((int(match.group("tile_id")), texture_match.group("name")))
    return tiles


def write_report(path: Path, records: dict[int, str]) -> None:
    lines = [
        f"{tile_id}=W,-1,{characters},{tile_id}"
        for tile_id, characters in sorted(records.items())
    ]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add tile wall records to an ECWolf WMC file from an XLAT and texture string table."
    )
    parser.add_argument("--xlat", type=Path, default=Path("xlat/O_Tst.txt"))
    parser.add_argument(
        "--texture-strings",
        type=Path,
        default=Path("MAPSYMBOLS/textures/texture_strings.txt"),
    )
    parser.add_argument("--output", type=Path, default=Path("generated_wall_strings.txt"))
    args = parser.parse_args()

    texture_strings = read_texture_strings(args.texture_strings)
    tiles = read_tiles(args.xlat)
    records = {}
    missing = []
    for tile_id, texture_name in tiles:
        characters = texture_strings.get(texture_name.casefold())
        if characters is None:
            missing.append((tile_id, texture_name))
        else:
            records[tile_id] = characters

    write_report(args.output, records)

    print(f"Parsed {len(tiles)} tiles; resolved {len(records)} texture strings.")
    print(f"Wrote {len(records)} lines to {args.output}.")
    print("The WMC file was not read or modified.")
    if missing:
        print(f"Missing texture strings ({len(missing)}):")
        for tile_id, texture_name in missing:
            print(f"  tile {tile_id}: {texture_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())