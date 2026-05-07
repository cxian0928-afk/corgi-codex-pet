#!/usr/bin/env python3
"""Validate a configurable Codex pet action manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

REQUIRED_STANDARD_ACTIONS = [
    "idle",
    "running-right",
    "running-left",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "running",
    "review",
]


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def detect_non_background_spans(source_path: Path, background_rgb: tuple[int, int, int]) -> list[list[int]]:
    spans: list[list[int]] = []
    with Image.open(source_path) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        start: int | None = None

        for x in range(width):
            column_has_foreground = False
            for y in range(height):
                if rgb.getpixel((x, y)) != background_rgb:
                    column_has_foreground = True
                    break
            if column_has_foreground and start is None:
                start = x
            elif not column_has_foreground and start is not None:
                spans.append([start, x - 1])
                start = None

        if start is not None:
            spans.append([start, width - 1])

    return spans


def validate_action(config: dict, config_dir: Path, action_name: str, action: dict) -> tuple[dict, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    source = action.get("source")
    frames = action.get("frames")
    slot_index = action.get("slotIndex")
    enabled = action.get("enabled", True)
    layout_mode = action.get("layoutMode") or config.get("sourceProcessing", {}).get("defaultLayoutMode", "equal-width")
    slice_boxes = action.get("sliceBoxes")
    background_rgb = tuple(config.get("sourceProcessing", {}).get("backgroundKeyRgb", [0, 255, 0]))

    summary = {
        "name": action_name,
        "enabled": enabled,
        "slotIndex": slot_index,
        "frames": frames,
        "source": source,
        "layoutMode": layout_mode,
    }

    if not source:
        errors.append("missing source path")
        return summary, errors, warnings

    source_path = (config_dir / source).resolve()
    if not source_path.exists():
        errors.append(f"missing file: {source_path}")
        return summary, errors, warnings

    if not isinstance(frames, int) or frames <= 0:
        errors.append("frames must be a positive integer")
        return summary, errors, warnings

    with Image.open(source_path) as image:
        width = image.width
        height = image.height

    summary["imageSize"] = {"width": width, "height": height}
    if layout_mode == "manual-slice-boxes":
        if not isinstance(slice_boxes, list) or len(slice_boxes) != frames:
            errors.append("manual-slice-boxes requires one [start, end] pair per frame")
        else:
            previous_end = -1
            normalized_boxes: list[list[int]] = []
            for box in slice_boxes:
                if not isinstance(box, list) or len(box) != 2:
                    errors.append("each slice box must be a [start, end] pair")
                    continue
                start, end = box
                if not isinstance(start, int) or not isinstance(end, int):
                    errors.append("slice box coordinates must be integers")
                    continue
                if start < 0 or end < start or end >= width:
                    errors.append(f"invalid slice box [{start}, {end}] for image width {width}")
                    continue
                if start <= previous_end:
                    errors.append("slice boxes must be ordered and non-overlapping")
                    continue
                previous_end = end
                normalized_boxes.append([start, end])

            if len(normalized_boxes) == frames:
                summary["sliceBoxes"] = normalized_boxes
                summary["detectedFrameWidths"] = [end - start + 1 for start, end in normalized_boxes]
    elif width % frames != 0:
        if layout_mode == "auto-detect-green-screen":
            spans = detect_non_background_spans(source_path, background_rgb)
            summary["detectedFrameBoxes"] = spans
            if len(spans) != frames:
                errors.append(
                    f"auto-detected {len(spans)} foreground spans, expected {frames}; "
                    "adjust the strip or add a custom slicing strategy"
                )
            else:
                summary["detectedFrameWidths"] = [end - start + 1 for start, end in spans]
        else:
            errors.append(f"image width {width} is not divisible by frame count {frames}")
    else:
        summary["frameWidth"] = width // frames

    if height <= 0:
        errors.append("image height must be positive")

    if enabled and slot_index is None:
        warnings.append("enabled action has no slotIndex; this is fine for custom unmapped actions")

    return summary, errors, warnings


def main() -> int:
    config_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "pet.config.json"
    config = load_config(config_path)
    config_dir = config_path.parent

    actions = config.get("actions", {})
    errors: list[str] = []
    warnings: list[str] = []
    summaries: list[dict] = []

    for action_name in REQUIRED_STANDARD_ACTIONS:
        if action_name not in actions:
            errors.append(f"missing required standard action: {action_name}")

    slot_indexes: dict[int, str] = {}
    for action_name, action in actions.items():
        summary, action_errors, action_warnings = validate_action(config, config_dir, action_name, action)
        summaries.append(summary)
        errors.extend(f"{action_name}: {message}" for message in action_errors)
        warnings.extend(f"{action_name}: {message}" for message in action_warnings)

        slot_index = action.get("slotIndex")
        if isinstance(slot_index, int):
            if slot_index in slot_indexes:
                errors.append(
                    f"slotIndex collision: {action_name} and {slot_indexes[slot_index]} both use {slot_index}"
                )
            else:
                slot_indexes[slot_index] = action_name

    result = {
        "ok": not errors,
        "config": str(config_path),
        "petId": config.get("pet", {}).get("id"),
        "actionCount": len(actions),
        "standardActionsPresent": [name for name in REQUIRED_STANDARD_ACTIONS if name in actions],
        "actions": summaries,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
