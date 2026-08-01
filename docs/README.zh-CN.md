# GeminiToGenius

面向 Antigravity 和 Antigravity IDE 中 Gemini 3.6 Flash (High) 的版本化专注运行框架。

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

它只把模型的注意力放在当前指令、活动窗口、相关文件和可验证结果上。

## 内容

- 12 个常驻指令文件
- 8 个生命周期钩子
- 4 个专用技能
- 从 `v1.0.0` 到 `v1.14.0` 的版本记录
- 不使用外部插件
- 只有在任务需要连接 MCP 时才使用 MCP

## 为什么这样做

常驻指令过长，容易被截断或失去约束力。这个项目把规则拆成短文件，生成一个入口文件，并保留每次修改的版本记录。

## 兼容范围

| 目标 | 支持版本 |
| --- | --- |
| Antigravity | `2.4.x` |
| Antigravity IDE | `2.1.x` |
| 模型目标 | `Gemini 3.6 Flash (High)` |

## 安装

以下命令适用于 macOS。顺序是 `clone → update → backup → install → verify`。先完成仓库更新，再备份现有配置。

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
cd GeminiToGenius
```

刚刚 clone 的仓库已经是最新状态。只有重复使用已有仓库时才需要更新。

```bash
cd GeminiToGenius && git pull --ff-only
```

覆盖配置前先备份。

```bash
BACKUP_DIR="$HOME/.gemini-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR" "$HOME/.gemini/config"
if [ -e "$HOME/.gemini/config/agy-focus" ] || [ -L "$HOME/.gemini/config/agy-focus" ]; then mv "$HOME/.gemini/config/agy-focus" "$BACKUP_DIR/agy-focus"; fi
if [ -e "$HOME/.gemini/GEMINI.md" ] || [ -L "$HOME/.gemini/GEMINI.md" ]; then mv "$HOME/.gemini/GEMINI.md" "$BACKUP_DIR/GEMINI.md"; fi
if [ -e "$HOME/.gemini/config/hooks.json" ] || [ -L "$HOME/.gemini/config/hooks.json" ]; then mv "$HOME/.gemini/config/hooks.json" "$BACKUP_DIR/hooks.json"; fi
if [ -e "$HOME/.gemini/config/skills" ] || [ -L "$HOME/.gemini/config/skills" ]; then mv "$HOME/.gemini/config/skills" "$BACKUP_DIR/skills"; fi
printf '%s\n' "$BACKUP_DIR"
```

最后输出的路径就是恢复点。备份后安装配置。

```bash
cp -a agy-focus "$HOME/.gemini/config/agy-focus"
ln -sfn versions/v1.14.0 "$HOME/.gemini/config/agy-focus/current"
ln -sfn config/agy-focus/current/GEMINI.md "$HOME/.gemini/GEMINI.md"
ln -sfn agy-focus/current/hooks/hooks.json "$HOME/.gemini/config/hooks.json"
ln -sfn agy-focus/current/skills "$HOME/.gemini/config/skills"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

正常结果应包含 `"ok": true`、`"rules": 12`、`"hooks": 8` 和 `"target": "Gemini 3.6 Flash (High)"`。安装后重启 Antigravity 或 Antigravity IDE。

## 更新

```bash
cd GeminiToGenius && git pull --ff-only
```

然后重新执行备份到验证的步骤。替换配置前必须先备份。

## 切换版本

```bash
find "$HOME/.gemini/config/agy-focus/versions" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V
ln -sfn versions/v1.12.0 "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

## 删除和恢复

```bash
REMOVED_DIR="$HOME/.gemini-removed-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REMOVED_DIR"
if [ -L "$HOME/.gemini/GEMINI.md" ]; then unlink "$HOME/.gemini/GEMINI.md"; fi
if [ -L "$HOME/.gemini/config/hooks.json" ]; then unlink "$HOME/.gemini/config/hooks.json"; fi
if [ -L "$HOME/.gemini/config/skills" ]; then unlink "$HOME/.gemini/config/skills"; fi
if [ -d "$HOME/.gemini/config/agy-focus" ]; then mv "$HOME/.gemini/config/agy-focus" "$REMOVED_DIR/agy-focus"; fi
printf '%s\n' "$REMOVED_DIR"
```

确认输出路径后再彻底删除：

```bash
rm -rf "$REMOVED_DIR"
```

恢复安装前的配置：

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/skills" "$HOME/.gemini/config/skills"
```

## UI 规则

- 禁止 AI Slop 文案、模糊标题和抽象魔法棒图标
- 禁止没有目的的悬停效果和微交互
- 禁止重复圆角卡片和机械式对称布局
- 不因习惯默认使用 `Inter` 或 `Roboto`
- 不把紫蓝霓虹渐变当作默认方案
- 优先检查内在尺寸、流体排版、非对称布局和移动优先响应式方案

## 许可证

MIT 许可证。请查看 [LICENSE](../LICENSE)。
