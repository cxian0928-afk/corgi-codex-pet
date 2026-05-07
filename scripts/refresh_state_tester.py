#!/usr/bin/env python3
"""Generate an atlas-based action tester that reads the final spritesheet directly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} 动作测试页</title>
  <style>
    :root {{
      --bg-a: #f8f0e2;
      --bg-b: #e7f4ef;
      --ink: #20312e;
      --muted: #60716d;
      --line: rgba(32,49,46,0.12);
      --card: rgba(255,255,255,0.84);
      --accent: #f69b49;
      --accent-2: #2d9b7a;
      --shadow: 0 18px 46px rgba(24, 38, 34, 0.14);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.78), transparent 34%),
        radial-gradient(circle at bottom right, rgba(246,155,73,0.18), transparent 30%),
        linear-gradient(135deg, var(--bg-a), var(--bg-b));
    }}
    .page {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 28px 18px 42px;
    }}
    .hero {{
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 20px;
      margin-bottom: 20px;
    }}
    .hero h1 {{
      margin: 0;
      font-size: clamp(28px, 4vw, 42px);
      line-height: 1.04;
    }}
    .hero p {{
      margin: 10px 0 0;
      max-width: 620px;
      line-height: 1.55;
      color: var(--muted);
    }}
    .tag {{
      white-space: nowrap;
      padding: 10px 14px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.72);
      font-weight: 700;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 20px;
    }}
    .panel {{
      border-radius: 24px;
      border: 1px solid var(--line);
      background: var(--card);
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
    }}
    .controls, .preview {{
      padding: 20px;
    }}
    .section-title {{
      margin: 0 0 16px;
      font-size: 15px;
      color: var(--muted);
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}
    .field {{
      margin-bottom: 14px;
    }}
    .field label {{
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 13px;
    }}
    select, input[type="range"] {{
      width: 100%;
    }}
    select {{
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px 14px;
      background: white;
      font-size: 15px;
    }}
    .buttons {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin: 16px 0;
    }}
    button {{
      border: 0;
      border-radius: 14px;
      padding: 12px 10px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 700;
      color: white;
      background: linear-gradient(135deg, var(--accent), #ff7f55);
    }}
    button.secondary {{
      background: linear-gradient(135deg, var(--accent-2), #1d7d61);
    }}
    button.ghost {{
      color: var(--ink);
      background: rgba(255,255,255,0.9);
      border: 1px solid var(--line);
    }}
    .meta {{
      padding: 14px 16px;
      border-radius: 16px;
      border: 1px dashed var(--line);
      background: rgba(255,255,255,0.7);
      line-height: 1.55;
      font-size: 14px;
    }}
    .meta strong {{
      display: inline-block;
      min-width: 78px;
    }}
    .stage {{
      min-height: 470px;
      border-radius: 26px;
      border: 1px solid var(--line);
      overflow: hidden;
      position: relative;
      display: grid;
      place-items: center;
      padding: 22px;
      background:
        linear-gradient(180deg, rgba(255,255,255,0.94), rgba(255,255,255,0.88)),
        repeating-linear-gradient(0deg, rgba(32,49,46,0.045) 0 1px, transparent 1px 24px),
        repeating-linear-gradient(90deg, rgba(32,49,46,0.045) 0 1px, transparent 1px 24px);
    }}
    .stage::after {{
      content: "";
      position: absolute;
      left: 10%;
      right: 10%;
      bottom: 24px;
      height: 28px;
      background: radial-gradient(ellipse at center, rgba(31, 42, 38, 0.18), transparent 70%);
      filter: blur(11px);
    }}
    canvas#previewCanvas {{
      width: min(100%, 360px);
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      position: relative;
      z-index: 1;
      filter: drop-shadow(0 12px 14px rgba(27, 36, 33, 0.14));
    }}
    .statusbar {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 16px;
    }}
    .chip {{
      padding: 8px 12px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.9);
      color: var(--muted);
      font-size: 13px;
    }}
    .filmstrip {{
      margin-top: 18px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(72px, 1fr));
      gap: 10px;
    }}
    .thumb {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(255,255,255,0.84);
      padding: 8px;
      cursor: pointer;
      text-align: center;
      transition: transform 120ms ease, border-color 120ms ease, background 120ms ease;
    }}
    .thumb.active {{
      transform: translateY(-2px);
      border-color: rgba(246,155,73,0.55);
      background: rgba(255,243,232,0.98);
    }}
    .thumb canvas {{
      width: 100%;
      image-rendering: pixelated;
      image-rendering: crisp-edges;
    }}
    .thumb span {{
      display: block;
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .hero {{ align-items: start; flex-direction: column; }}
      .buttons {{ grid-template-columns: repeat(2, 1fr); }}
      .stage {{ min-height: 350px; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div>
        <h1>{title} 动作测试页</h1>
        <p>这个版本直接读取最终的 <code>package/spritesheet.webp</code>。以后你只要手改 atlas 并保存同一路径，刷新这个页面就能看到最新动作，不需要重新拆帧。</p>
      </div>
      <div class="tag">Atlas Live Preview</div>
    </section>
    <div class="layout">
      <section class="panel controls">
        <h2 class="section-title">控制面板</h2>
        <div class="field">
          <label for="stateSelect">动作状态</label>
          <select id="stateSelect"></select>
        </div>
        <div class="field">
          <label for="speedRange">播放速度: <span id="speedLabel"></span></label>
          <input id="speedRange" type="range" min="2" max="16" step="1" value="8" />
        </div>
        <div class="buttons">
          <button id="togglePlay">暂停</button>
          <button class="secondary" id="stepButton">单步</button>
          <button class="ghost" id="randomButton">随机</button>
          <button class="ghost" id="reloadAtlas">重载图集</button>
        </div>
        <div class="meta">
          <div><strong>当前状态</strong><span id="metaState"></span></div>
          <div><strong>当前帧</strong><span id="metaFrame"></span></div>
          <div><strong>总帧数</strong><span id="metaCount"></span></div>
          <div><strong>备注</strong><span id="metaNotes"></span></div>
        </div>
      </section>
      <section class="panel preview">
        <h2 class="section-title">预览</h2>
        <div class="stage">
          <canvas id="previewCanvas" width="{cell_width}" height="{cell_height}"></canvas>
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
    const CONFIG = {config_json};
    const previewCanvas = document.getElementById('previewCanvas');
    const previewContext = previewCanvas.getContext('2d');
    const stateSelect = document.getElementById('stateSelect');
    const speedRange = document.getElementById('speedRange');
    const speedLabel = document.getElementById('speedLabel');
    const togglePlay = document.getElementById('togglePlay');
    const stepButton = document.getElementById('stepButton');
    const randomButton = document.getElementById('randomButton');
    const reloadAtlas = document.getElementById('reloadAtlas');
    const metaState = document.getElementById('metaState');
    const metaFrame = document.getElementById('metaFrame');
    const metaCount = document.getElementById('metaCount');
    const metaNotes = document.getElementById('metaNotes');
    const chipStatus = document.getElementById('chipStatus');
    const chipFps = document.getElementById('chipFps');
    const chipFrames = document.getElementById('chipFrames');
    const filmstrip = document.getElementById('filmstrip');

    const atlas = new Image();
    let atlasLoaded = false;
    let currentState = CONFIG.actions[0].name;
    let currentFrame = 0;
    let playing = true;
    let lastTick = 0;

    function atlasUrl() {{
      return CONFIG.atlasPath + '?ts=' + Date.now();
    }}

    function loadAtlas() {{
      atlasLoaded = false;
      atlas.src = atlasUrl();
    }}

    atlas.onload = () => {{
      atlasLoaded = true;
      updateView();
    }};

    function getAction(name) {{
      return CONFIG.actions.find((action) => action.name === name) || CONFIG.actions[0];
    }}

    function frameRect(action, frameIndex) {{
      return {{
        sx: frameIndex * CONFIG.cellWidth,
        sy: action.slotIndex * CONFIG.cellHeight,
        sw: CONFIG.cellWidth,
        sh: CONFIG.cellHeight,
      }};
    }}

    function drawFrame(canvas, action, frameIndex) {{
      const context = canvas.getContext('2d');
      const rect = frameRect(action, frameIndex);
      context.clearRect(0, 0, canvas.width, canvas.height);
      if (!atlasLoaded) {{
        context.fillStyle = '#7a8b87';
        context.font = '12px sans-serif';
        context.fillText('loading...', 8, 18);
        return;
      }}
      context.drawImage(
        atlas,
        rect.sx, rect.sy, rect.sw, rect.sh,
        0, 0, canvas.width, canvas.height
      );
    }}

    function renderFilmstrip(action) {{
      filmstrip.innerHTML = '';
      for (let index = 0; index < action.frames; index += 1) {{
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'thumb' + (index === currentFrame ? ' active' : '');
        const canvas = document.createElement('canvas');
        canvas.width = CONFIG.cellWidth;
        canvas.height = CONFIG.cellHeight;
        drawFrame(canvas, action, index);
        const label = document.createElement('span');
        label.textContent = String(index + 1);
        button.appendChild(canvas);
        button.appendChild(label);
        button.addEventListener('click', () => {{
          currentFrame = index;
          playing = false;
          togglePlay.textContent = '播放';
          updateView();
        }});
        filmstrip.appendChild(button);
      }}
    }}

    function updateView() {{
      const action = getAction(currentState);
      const fps = Number(speedRange.value);
      speedLabel.textContent = `${{fps}} fps`;
      drawFrame(previewCanvas, action, currentFrame);
      metaState.textContent = action.name;
      metaFrame.textContent = `${{currentFrame + 1}} / ${{action.frames}}`;
      metaCount.textContent = String(action.frames);
      metaNotes.textContent = action.notes || '无';
      chipStatus.textContent = playing ? '播放中' : '已暂停';
      chipFps.textContent = `速度 ${{fps}} fps`;
      chipFrames.textContent = `共 ${{action.frames}} 帧`;
      renderFilmstrip(action);
    }}

    function tick(timestamp) {{
      const action = getAction(currentState);
      const fps = Number(speedRange.value);
      const frameDuration = 1000 / fps;
      if (playing && timestamp - lastTick >= frameDuration) {{
        currentFrame = (currentFrame + 1) % action.frames;
        lastTick = timestamp;
        updateView();
      }}
      requestAnimationFrame(tick);
    }}

    for (const action of CONFIG.actions) {{
      const option = document.createElement('option');
      option.value = action.name;
      option.textContent = `${{action.name}} (${{action.frames}} 帧)`;
      stateSelect.appendChild(option);
    }}

    stateSelect.addEventListener('change', () => {{
      currentState = stateSelect.value;
      currentFrame = 0;
      updateView();
    }});

    speedRange.addEventListener('input', updateView);

    togglePlay.addEventListener('click', () => {{
      playing = !playing;
      togglePlay.textContent = playing ? '暂停' : '播放';
      lastTick = performance.now();
      updateView();
    }});

    stepButton.addEventListener('click', () => {{
      const action = getAction(currentState);
      playing = false;
      togglePlay.textContent = '播放';
      currentFrame = (currentFrame + 1) % action.frames;
      updateView();
    }});

    randomButton.addEventListener('click', () => {{
      const action = CONFIG.actions[Math.floor(Math.random() * CONFIG.actions.length)];
      currentState = action.name;
      stateSelect.value = action.name;
      currentFrame = 0;
      updateView();
    }});

    reloadAtlas.addEventListener('click', () => {{
      loadAtlas();
    }});

    stateSelect.value = currentState;
    loadAtlas();
    updateView();
    requestAnimationFrame(tick);
  </script>
</body>
</html>
"""


def build_tester_config(config: dict) -> dict:
    atlas = config.get("atlas", {})
    actions = []
    for action_name in config.get("standardActionsOrder", []):
        action = config["actions"].get(action_name)
        if not action or not action.get("enabled", True):
            continue
        actions.append(
            {
                "name": action_name,
                "slotIndex": int(action["slotIndex"]),
                "frames": int(action["frames"]),
                "notes": action.get("notes", ""),
            }
        )
    return {
        "atlasPath": "package/spritesheet.webp",
        "cellWidth": int(atlas.get("cellWidth", 192)),
        "cellHeight": int(atlas.get("cellHeight", 208)),
        "actions": actions,
    }


def write_tester(config_path: Path, output_path: Path) -> Path:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    tester_config = build_tester_config(config)
    html = HTML_TEMPLATE.format(
        title=config["pet"]["displayName"],
        cell_width=tester_config["cellWidth"],
        cell_height=tester_config["cellHeight"],
        config_json=json.dumps(tester_config, ensure_ascii=False),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=str(Path(__file__).resolve().parents[1] / "pet.config.json"),
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[1] / "build" / "state-tester.html"),
    )
    args = parser.parse_args()

    written = write_tester(
        Path(args.config).expanduser().resolve(),
        Path(args.output).expanduser().resolve(),
    )
    print(json.dumps({"ok": True, "stateTester": str(written)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
