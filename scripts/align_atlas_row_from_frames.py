#!/usr/bin/env python3
"""Align a sequence of frame PNGs and patch one atlas row in place."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from PIL import Image


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise SystemExit("frame has no visible pixels")
    return bbox


def align_frame_to_cell(
    source: Image.Image,
    cell_width: int,
    cell_height: int,
    target_center_x: int,
    top_offset: int,
    bottom_offset: int | None,
) -> tuple[Image.Image, dict[str, int | float]]:
    bbox = alpha_bbox(source)
    left, top, right, bottom = bbox
    bbox_center_x = (left + right) / 2
    paste_x = round(target_center_x - bbox_center_x)
    paste_y = top_offset - top if bottom_offset is None else bottom_offset - bottom

    cell = Image.new("RGBA", (cell_width, cell_height), (0, 0, 0, 0))
    cell.alpha_composite(source, (paste_x, paste_y))
    aligned_bbox = alpha_bbox(cell)
    return cell, {
        "source_left": left,
        "source_right": right,
        "source_center_x": bbox_center_x,
        "source_top": top,
        "source_bottom": bottom,
        "paste_x": paste_x,
        "paste_y": paste_y,
        "aligned_top": aligned_bbox[1],
        "aligned_bottom": aligned_bbox[3],
        "aligned_left": aligned_bbox[0],
        "aligned_right": aligned_bbox[2],
        "aligned_center_x": (aligned_bbox[0] + aligned_bbox[2]) / 2,
    }


def fit_source_to_cell(
    source: Image.Image,
    cell_width: int,
    cell_height: int,
    padding: int = 10,
) -> Image.Image:
    bbox = alpha_bbox(source)
    sprite = source.crop(bbox)
    max_width = cell_width - padding
    max_height = cell_height - padding
    scale = min(max_width / sprite.width, max_height / sprite.height, 1.0)
    if scale != 1.0:
        sprite = sprite.resize(
            (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))),
            Image.Resampling.LANCZOS,
        )
    target = Image.new("RGBA", (cell_width, cell_height), (0, 0, 0, 0))
    left = (cell_width - sprite.width) // 2
    top = (cell_height - sprite.height) // 2
    target.alpha_composite(sprite, (left, top))
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas", required=True)
    parser.add_argument("--row-index", required=True, type=int)
    parser.add_argument("--inputs", nargs="+", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cell-width", type=int, default=192)
    parser.add_argument("--cell-height", type=int, default=208)
    parser.add_argument("--top-offset", type=int, default=12)
    parser.add_argument("--bottom-offset", type=int)
    parser.add_argument("--target-center-x", type=int)
    parser.add_argument("--fit-source-to-cell", action="store_true")
    parser.add_argument("--mirror-horizontal", action="store_true")
    args = parser.parse_args()

    frame_paths = [Path(raw).expanduser().resolve() for raw in args.inputs]
    raw_sources = [Image.open(path).convert("RGBA") for path in frame_paths]
    if args.mirror_horizontal:
        raw_sources = [image.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for image in raw_sources]
    sources = [
        fit_source_to_cell(image, args.cell_width, args.cell_height)
        if args.fit_source_to_cell
        else image
        for image in raw_sources
    ]
    source_bboxes = [alpha_bbox(image) for image in sources]
    centers = [(left + right) / 2 for left, _top, right, _bottom in source_bboxes]
    target_center_x = (
        args.target_center_x if args.target_center_x is not None else round(statistics.median(centers))
    )

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    aligned_cells: list[Image.Image] = []
    report: list[dict[str, int | float | str]] = []
    for index, (path, source) in enumerate(zip(frame_paths, sources, strict=True)):
        cell, meta = align_frame_to_cell(
            source,
            args.cell_width,
            args.cell_height,
            target_center_x,
            args.top_offset,
            args.bottom_offset,
        )
        aligned_cells.append(cell)
        frame_output = output_dir / f"{index:02d}.png"
        cell.save(frame_output)
        meta["file"] = path.name
        report.append(meta)

    atlas_path = Path(args.atlas).expanduser().resolve()
    with Image.open(atlas_path) as atlas_opened:
        atlas = atlas_opened.convert("RGBA")

    for column, cell in enumerate(aligned_cells):
        left = column * args.cell_width
        top = args.row_index * args.cell_height
        atlas.paste((0, 0, 0, 0), (left, top, left + args.cell_width, top + args.cell_height))
        atlas.alpha_composite(cell, (left, top))

    save_kwargs: dict[str, object] = {}
    if atlas_path.suffix.lower() == ".webp":
        save_kwargs = {"format": "WEBP", "lossless": True, "quality": 100, "method": 6}
    atlas.save(atlas_path, **save_kwargs)

    result = {
        "ok": True,
        "atlas": str(atlas_path),
        "rowIndex": args.row_index,
        "targetCenterX": target_center_x,
        "outputDir": str(output_dir),
        "mirrorHorizontal": args.mirror_horizontal,
        "frames": report,
    }
    (output_dir / "alignment-report.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
