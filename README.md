# 柯基宠物脚手架

这个目录保存了柯基宠物的可配置资源结构，方便你以后替换动作、补充动作，或者重新打包，而不用改主流程代码。

## 目录结构

- `pet.config.json`
  这是一份总配置文件，保存宠物信息、动作顺序、帧数、切帧方式和素材路径。
- `assets/actions/*.png`
  这里是你提供的原始动作条和静态参考图。
- `scripts/validate_pet_config.py`
  用来检查配置是否正确，包括：
  - 动作文件是否存在
  - 标准动作是否齐全
  - `slotIndex` 是否冲突
  - 图片宽度和帧数是否匹配
  - 手工切帧框是否有效
- `scripts/build_pet_package.py`
  用来把动作条切成单帧、去掉绿色背景、缩放到 Codex 标准格子里，并生成最终宠物包和测试页面。

## 切帧接口说明

这套脚手架支持多种动作条切帧方式。

- `layoutMode: "auto-detect-green-screen"`
  适合动作之间有明显绿色空隙的图片。脚本会把纯绿背景当作空白区域，自动识别每一帧的位置。
- `layoutMode: "manual-slice-boxes"`
  适合动作贴得比较紧、自动识别不稳定的图片。你可以手动提供每一帧的横向裁切范围 `[start, end]`。
- 等宽切帧
  如果一张动作图本身就是严格等宽分帧，脚本也可以直接按等宽方式处理。

## 替换已有动作

1. 把对应 PNG 替换到 `assets/actions/` 目录里。
2. 保持 `pet.config.json` 里的动作 key 不变。
3. 如果帧数、路径、备注有变化，就同步修改配置。
4. 运行：

```bash
python scripts/validate_pet_config.py
```

5. 再运行：

```bash
python scripts/build_pet_package.py
```

## 新增动作

1. 把新动作图放到 `assets/actions/custom/`，或者你自己指定的新目录。
2. 在 `pet.config.json` 的 `actions` 里新增一条配置。
3. 如果这个动作还没有映射到标准 9 行 atlas，可以先设置：

```json
"slotIndex": null
```

4. 运行配置校验脚本确认无误。

## 构建本地宠物包

运行：

```bash
python scripts/build_pet_package.py
```

构建结果会输出到：

- `build/spritesheet.png`
  最终 atlas 的 PNG 版本
- `build/frames/<action>/`
  每个动作拆好的单帧 PNG
- `build/package/spritesheet.webp`
  最终宠物包使用的贴图
- `build/package/pet.json`
  最终宠物清单文件
- `build/state-tester.html`
  本地动作测试页面

## 测试不同动作

打开：

- `build/state-tester.html`

你可以直接测试：

- 切换不同动作状态
- 暂停播放
- 单步查看每一帧
- 调整播放速度
- 查看当前动作的所有缩略帧

以后只要你替换动作图并重新构建，这个测试页也会自动更新。

如果你是直接手改最终 atlas：

```bash
python scripts/refresh_state_tester.py
```

这个脚本会把测试页改成直接读取 `build/package/spritesheet.webp` 的版本。之后你只要覆盖 atlas 并刷新页面，就能看到新动作，不需要重新拆帧。

## 当前备注

- `waiting` 当前被标记为 `needs-review`，因为它现在的表现更接近 `idle`，以后可以再优化成更明确的“等待中”动作。
- `running` 当前使用了笔记本道具，所以这个动作已经带有“办公中 / 工作中”的设定。
- `failed` 当前已经可用；如果以后重做，建议继续让眼泪贴近脸部，避免变成漂浮特效。
