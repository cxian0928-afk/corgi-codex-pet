#!/usr/bin/env python3
"""Build a local Codex pet package from pet.config.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

CELL_WIDTH = 192
CELL_HEIGHT = 208
ATLAS_COLUMNS = 8
ATLAS_ROWS = 9
ATLAS_WIDTH = ATLAS_COLUMNS * CELL_WIDTH
ATLAS_HEIGHT = ATLAS_ROWS * CELL_HEIGHT

STATE_TESTER_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} Action Tester</title>
  <style>
    :root {{
      --bg-a: #f6efe3;
      --bg-b: #e7f6ef;
      --ink: #1d2b28;
      --muted: #5d706c;
      --card: rgba(255,255,255,0.82);
      --line: rgba(29,43,40,0.12);
      --accent: #ff9e45;
      --accent-2: #2a9d78;
      --shadow: 0 18px 48px rgba(28, 42, 37, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.75), transparent 36%),
        radial-gradient(circle at bottom right, rgba(255,185,106,0.34), transparent 30%),
        linear-gradient(135deg, var(--bg-a), var(--bg-b));
      min-height: 100vh;
    }}
    .page {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .hero {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 20px;
      margin-bottom: 22px;
    }}
    .hero h1 {{
      margin: 0;
      font-size: clamp(28px, 4vw, 44px);
      line-height: 1.02;
    }}
    .hero p {{
      margin: 10px 0 0;
      color: var(--muted);
      max-width: 620px;
      line-height: 1.5;
    }}
    .pill {{
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.7);
      padding: 10px 14px;
      border-radius: 999px;
      font-weight: 600;
      white-space: nowrap;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 22px;
    }}
    .panel {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 24px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }}
    .controls {{
      padding: 20px;
    }}
    .controls h2,
    .preview h2 {{
      margin: 0 0 16px;
      font-size: 16px;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .field {{
      margin-bottom: 14px;
    }}
    .field label {{
      display: block;
      margin-bottom: 8px;
      font-size: 13px;
      color: var(--muted);
    }}
    select,
    input[type="range"] {{
      width: 100%;
    }}
    select {{
      appearance: none;
      border: 1px solid var(--line);
      background: white;
      padding: 12px 14px;
      border-radius: 14px;
      font-size: 15px;
    }}
    .buttons {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin: 16px 0 14px;
    }}
    button {{
      border: 0;
      border-radius: 14px;
      padding: 12px 12px;
      font-size: 14px;
      font-weight: 700;
      color: white;
      background: linear-gradient(135deg, var(--accent), #ff7d4d);
      cursor: pointer;
    }}
    button.secondary {{
      background: linear-gradient(135deg, var(--accent-2), #1f7a5f);
    }}
    button.ghost {{
      color: var(--ink);
      background: rgba(255,255,255,0.9);
      border: 1px solid var(--line);
    }}
    .meta {{
      padding: 14px 16px;
      background: rgba(255,255,255,0.72);
      border-radius: 16px;
      border: 1px dashed var(--line);
      line-height: 1.5;
      font-size: 14px;
    }}
    .meta strong {{
      display: inline-block;
      min-width: 72px;
    }}
    .preview {{
      padding: 20px;
    }}
    .stage {{
      min-height: 480px;
      border-radius: 28px;
      position: relative;
      overflow: hidden;
      background:
        linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,255,255,0.9)),
        repeating-linear-gradient(
          0deg,
          rgba(33, 52, 47, 0.04) 0px,
          rgba(33, 52, 47, 0.04) 1px,
          transparent 1px,
          transparent 24px
        ),
        repeating-linear-gradient(
          90deg,
          rgba(33, 52, 47, 0.04) 0px,
          rgba(33, 52, 47, 0.04) 1px,
          transparent 1px,
          transparent 24px
        );
      border: 1px solid var(--line);
      display: grid;
      place-items: center;
      padding: 24px;
    }}
    .stage::after {{
      content: "";
      position: absolute;
      inset: auto 10% 22px;
      height: 28px;
      background: radial-gradient(ellipse at center, rgba(36,45,41,0.18), transparent 70%);
      filter: blur(10px);
    }}
    .sprite-shell {{
      position: relative;
      z-index: 1;
      width: min(100%, 460px);
      aspect-ratio: 1 / 1;
      display: grid;
      place-items: center;
    }}
    .sprite-shell img {{
      width: min(100%, 360px);
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      filter: drop-shadow(0 12px 14px rgba(30, 40, 36, 0.12));
    }}
    .statusbar {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 16px;
    }}
    .chip {{
      background: rgba(255,255,255,0.9);
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 13px;
      color: var(--muted);
    }}
    .filmstrip {{
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(70px, 1fr));
      gap: 10px;
    }}
    .thumb {{
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.84);
      border-radius: 16px;
      padding: 8px;
      text-align: center;
      cursor: pointer;
      transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
    }}
    .thumb.active {{
      border-color: rgba(255, 125, 77, 0.5);
      background: rgba(255, 242, 232, 0.95);
      transform: translateY(-2px);
    }}
    .thumb img {{
      width: 100%;
      image-rendering: pixelated;
      image-rendering: crisp-edges;
    }}
    .thumb span {{
      display: block;
      margin-top: 6px;
      font-size: 12px;
      color: var(--muted);
    }}
    @media (max-width: 860px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .hero {{ align-items: start; flex-direction: column; }}
      .stage {{ min-height: 360px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div>
        <h1>{title} Action Tester</h1>
        <p>切换不同状态，检查循环节奏、单帧姿态和动作一致性。以后你替换 PNG 或新增动作后，重新构建一次，这个测试页也会一起更新。</p>
      </div>
      <div class="pill">Built for {pet_id}</div>
    </section>
    <div class="layout">
      <section class="panel controls">
        <h2>Controls</h2>
        <div class="field">
          <label for="stateSelect">动作状态</label>
          <select id="stateSelect"></select>
        </div>
        <div class="field">
          <label for="speedRange">播放速度: <span id="speedLabel"></span></label>
          <input id="speedRange" type="range" min="2" max="16" step="1" value="8" />
        </div>
        <div class="buttons">
          <button id="togglePlay">Pause</button>
          <button class="secondary" id="stepButton">Step</button>
          <button class="ghost" id="randomButton">Random</button>
        </div>
        <div class="meta">
          <div><strong>当前状态</strong><span id="metaState"></span></div>
          <div><strong>当前帧</strong><span id="metaFrame"></span></div>
          <div><strong>总帧数</strong><span id="metaCount"></span></div>
          <div><strong>备注</strong><span id="metaNotes"></span></div>
        </div>
      </section>
      <section class="panel preview">
        <h2>Preview</h2>
        <div class="stage">
          <div class="sprite-shell">
            <img id="sprite" alt="pet action preview" />
          </div>
        </div>
        <div class="statusbar">
          <div class="chip" id="chipStatus"></div>
          <div class="chip" id="chipFps"></div>
          <div class="chip" id="chipFrames"></div>
        </div>
        <div class="filmstrip" id="filmstrip"></div>
      </section>
    </div>
  </div>
  <script>
    const ACTIONS = {actions_json};
    const stateSelect = document.getElementById('stateSelect');
    const speedRange = document.getElementById('speedRange');
    const speedLabel = document.getElementById('speedLabel');
    const sprite = document.getElementById('sprite');
    const togglePlay = document.getElementById('togglePlay');
    const stepButton = document.getElementById('stepButton');
    const randomButton = document.getElementById('randomButton');
    const metaState = document.getElementById('metaState');
    const metaFrame = document.getElementById('metaFrame');
    const metaCount = document.getElementById('metaCount');
    const metaNotes = document.getElementById('metaNotes');
    const chipStatus = document.getElementById('chipStatus');
    const chipFps = document.getElementById('chipFps');
    const chipFrames = document.getElementById('chipFrames');
    const filmstrip = document.getElementById('filmstrip');

    let currentState = ACTIONS[0].name;
    let currentFrame = 0;
    let playing = true;
    let lastTick = 0;

    for (const action of ACTIONS) {{
      const option = document.createElement('option');
      option.value = action.name;
      option.textContent = `${{action.name}} (${{action.frames.length}} 帧)`;
      stateSelect.appendChild(option);
    }}

    function getAction(name) {{
      return ACTIONS.find((action) => action.name === name) || ACTIONS[0];
    }}

    function frameSrc(action, index) {{
      return action.frames[index];
    }}

    function renderFilmstrip(action) {{
      filmstrip.innerHTML = '';
      action.frames.forEach((src, index) => {{
        const button = document.createElement('button');
        button.className = 'thumb' + (index === currentFrame ? ' active' : '');
        button.type = 'button';
        button.innerHTML = `<img src="${{src}}" alt="${{action.name}} frame ${{index + 1}}" /><span>${{index + 1}}</span>`;
        button.addEventListener('click', () => {{
          currentFrame = index;
          playing = false;
          togglePlay.textContent = 'Play';
          updateView();
        }});
        filmstrip.appendChild(button);
      }});
    }}

    function updateView() {{
      const action = getAction(currentState);
      const fps = Number(speedRange.value);
      speedLabel.textContent = `${{fps}} fps`;
      sprite.src = frameSrc(action, currentFrame);
      metaState.textContent = action.name;
      metaFrame.textContent = `${{currentFrame + 1}} / ${{action.frames.length}}`;
      metaCount.textContent = String(action.frames.length);
      metaNotes.textContent = action.notes || 'No notes';
      chipStatus.textContent = playing ? '播放中' : '已暂停';
      chipFps.textContent = `速度 ${{fps}} fps`;
      chipFrames.textContent = `共 ${{action.frames.length}} 帧`;
      renderFilmstrip(action);
    }}

    function tick(timestamp) {{
      const action = getAction(currentState);
      const fps = Number(speedRange.value);
      const frameDuration = 1000 / fps;
      if (playing && timestamp - lastTick >= frameDuration) {{
        currentFrame = (currentFrame + 1) % action.frames.length;
        lastTick = timestamp;
        updateView();
      }}
      requestAnimationFrame(tick);
    }}

    stateSelect.addEventListener('change', () => {{
      currentState = stateSelect.value;
      currentFrame = 0;
      updateView();
    }});

    speedRange.addEventListener('input', updateView);

    togglePlay.addEventListener('click', () => {{
      playing = !playing;
      togglePlay.textContent = playing ? 'Pause' : 'Play';
      lastTick = performance.now();
      updateView();
    }});

    stepButton.addEventListener('click', () => {{
      const action = getAction(currentState);
      playing = false;
      togglePlay.textContent = 'Play';
      currentFrame = (currentFrame + 1) % action.frames.length;
      updateView();
    }});

    randomButton.addEventListener('click', () => {{
      const action = ACTIONS[Math.floor(Math.random() * ACTIONS.length)];
      currentState = action.name;
      stateSelect.value = action.name;
      currentFrame = 0;
      updateView();
    }});

    stateSelect.value = currentState;
    updateView();
    requestAnimationFrame(tick);
  </script>
</body>
</html>
"""


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def remove_background(
    image: Image.Image,
    background_rgb: tuple[int, int, int],
    tolerance: int,
    dominance_threshold: int,
) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            red, green, blue, alpha = pixels[x, y]
            exactish_match = (
                abs(red - background_rgb[0]) <= tolerance
                and abs(green - background_rgb[1]) <= tolerance
                and abs(blue - background_rgb[2]) <= tolerance
            )
            green_dominant = (
                green >= 160
                and green - red >= dominance_threshold
                and green - blue >= dominance_threshold
            )
            if exactish_match or green_dominant:
                pixels[x, y] = (0, 0, 0, 0)
    return rgba


def fit_to_cell(image: Image.Image) -> Image.Image:
    target = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
    alpha_bbox = image.getchannel("A").getbbox()
    if alpha_bbox is None:
        return target

    sprite = image.crop(alpha_bbox)
    max_width = CELL_WIDTH - 10
    max_height = CELL_HEIGHT - 10
    scale = min(max_width / sprite.width, max_height / sprite.height, 1.0)
    if scale != 1.0:
        sprite = sprite.resize(
            (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale))),
            Image.Resampling.LANCZOS,
        )

    left = (CELL_WIDTH - sprite.width) // 2
    top = (CELL_HEIGHT - sprite.height) // 2
    target.alpha_composite(sprite, (left, top))
    return target


def detect_non_background_spans(
    image: Image.Image,
    background_rgb: tuple[int, int, int],
) -> list[tuple[int, int]]:
    rgb = image.convert("RGB")
    spans: list[tuple[int, int]] = []
    start: int | None = None

    for x in range(rgb.width):
        column_has_foreground = False
        for y in range(rgb.height):
            if rgb.getpixel((x, y)) != background_rgb:
                column_has_foreground = True
                break
        if column_has_foreground and start is None:
            start = x
        elif not column_has_foreground and start is not None:
            spans.append((start, x - 1))
            start = None

    if start is not None:
        spans.append((start, rgb.width - 1))
    return spans


def slice_boxes_for_action(
    image: Image.Image,
    action: dict,
    background_rgb: tuple[int, int, int],
) -> list[tuple[int, int]]:
    frames = action["frames"]
    layout_mode = action.get("layoutMode", "equal-width")
    manual_boxes = action.get("sliceBoxes")

    if layout_mode == "manual-slice-boxes":
        return [(int(start), int(end)) for start, end in manual_boxes]

    if image.width % frames == 0:
        frame_width = image.width // frames
        return [
            (index * frame_width, ((index + 1) * frame_width) - 1)
            for index in range(frames)
        ]

    if layout_mode == "auto-detect-green-screen":
        spans = detect_non_background_spans(image, background_rgb)
        if len(spans) == frames:
            return spans

    raise SystemExit(
        f"could not determine frame boxes for action {action.get('source')}; "
        f"layoutMode={layout_mode}, frames={frames}, width={image.width}"
    )


def extract_action_frames(
    image_path: Path,
    action: dict,
    background_rgb: tuple[int, int, int],
    tolerance: int,
    dominance_threshold: int,
) -> list[Image.Image]:
    with Image.open(image_path) as opened:
        source = opened.convert("RGBA")

    boxes = slice_boxes_for_action(source, action, background_rgb)
    frames: list[Image.Image] = []
    for left, end in boxes:
        crop = source.crop((left, 0, end + 1, source.height))
        transparent = remove_background(crop, background_rgb, tolerance, dominance_threshold)
        frames.append(fit_to_cell(transparent))
    return frames


def compose_atlas(config: dict, config_dir: Path, frames_dir: Path) -> Image.Image:
    atlas = Image.new("RGBA", (ATLAS_WIDTH, ATLAS_HEIGHT), (0, 0, 0, 0))
    background_rgb = tuple(config.get("sourceProcessing", {}).get("backgroundKeyRgb", [0, 255, 0]))
    tolerance = int(config.get("sourceProcessing", {}).get("backgroundTolerance", 0))
    dominance_threshold = int(config.get("sourceProcessing", {}).get("backgroundDominanceThreshold", 60))

    for action_name in config.get("standardActionsOrder", []):
        action = config["actions"][action_name]
        if not action.get("enabled", True):
            continue

        action_path = (config_dir / action["source"]).resolve()
        row_index = int(action["slotIndex"])
        frames = extract_action_frames(
            action_path,
            action,
            background_rgb,
            tolerance,
            dominance_threshold,
        )

        action_frames_dir = frames_dir / action_name
        action_frames_dir.mkdir(parents=True, exist_ok=True)
        for column_index, frame in enumerate(frames):
            left = column_index * CELL_WIDTH
            top = row_index * CELL_HEIGHT
            atlas.alpha_composite(frame, (left, top))
            frame.save(action_frames_dir / f"{column_index:02d}.png")

    return atlas


def write_pet_manifest(config: dict, target_dir: Path) -> Path:
    manifest = {
        "id": config["pet"]["id"],
        "displayName": config["pet"]["displayName"],
        "description": config["pet"]["description"],
        "spritesheetPath": "spritesheet.webp",
    }
    manifest_path = target_dir / "pet.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def write_state_tester(config: dict, output_dir: Path) -> Path:
    actions_data: list[dict[str, object]] = []
    for action_name in config.get("standardActionsOrder", []):
        action = config["actions"][action_name]
        if not action.get("enabled", True):
            continue
        frame_count = int(action["frames"])
        action_frames = [
            f"frames/{action_name}/{index:02d}.png"
            for index in range(frame_count)
        ]
        actions_data.append(
            {
                "name": action_name,
                "notes": action.get("notes", ""),
                "frames": action_frames,
            }
        )

    html = STATE_TESTER_HTML.format(
        title=config["pet"]["displayName"],
        pet_id=config["pet"]["id"],
        actions_json=json.dumps(actions_data, ensure_ascii=False),
    )
    target = output_dir / "state-tester.html"
    target.write_text(html, encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "pet.config.json"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "build"),
    )
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    config = load_config(config_path)
    config_dir = config_path.parent

    frames_dir = output_dir / "frames"
    package_dir = output_dir / "package"
    atlas_png = output_dir / "spritesheet.png"
    atlas_webp = package_dir / "spritesheet.webp"

    frames_dir.mkdir(parents=True, exist_ok=True)
    package_dir.mkdir(parents=True, exist_ok=True)

    atlas = compose_atlas(config, config_dir, frames_dir)
    atlas.save(atlas_png)
    atlas.save(atlas_webp, format="WEBP", lossless=True, quality=100, method=6)
    manifest_path = write_pet_manifest(config, package_dir)
    tester_path = write_state_tester(config, output_dir)

    result = {
        "ok": True,
        "config": str(config_path),
        "spritesheetPng": str(atlas_png),
        "spritesheetWebp": str(atlas_webp),
        "manifest": str(manifest_path),
        "framesDir": str(frames_dir),
        "stateTester": str(tester_path),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
