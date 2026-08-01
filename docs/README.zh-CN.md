# GeminiToGenius

> Gemini 在实际工作里越来越不靠谱，所以做了这个。它就是一套护栏。

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

面向 Antigravity 和 Antigravity IDE 中 Gemini 3.6 Flash (High) 的全局规则、钩子和技能。

## 首次安装

macOS 上执行这一行：

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

脚本按顺序执行：`git pull --ff-only`、把现有配置移到带时间戳的备份目录、安装当前配置、运行验证。

不使用 `curl | sh`。先 clone，再运行本地脚本。需要 `git`、`python3` 和 `rsync`。出现 `Installed agy-focus v...` 后重启 Antigravity 或 Antigravity IDE。

## 内容

| 项目 | 当前值 |
| --- | --- |
| 目标模型 | Gemini 3.6 Flash (High) |
| 常驻规则 | 12 |
| 生命周期钩子 | 13 |
| 自动技能 | 8 |
| 外部插件 | 无 |
| MCP | 仅当连接本身就是任务目标 |

普通自然语言会自动路由，不需要 `/` 或 `@`。

## 已安装用户更新

在旧 clone 中运行同一脚本：

```bash
cd /path/to/GeminiToGenius
bash scripts/install.sh
```

脚本先更新 checkout，所以旧安装会切换到当前配置。如果有 tracked 改动，脚本会在 `git pull` 前停止；请先 commit、stash 或整理改动。

每次运行都会输出类似的备份路径：

```text
/Users/you/.gemini-backup-YYYYMMDD-HHMMSS
```

## 验证安装

```bash
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/test_hook_runner.py"
```

看到 `"ok": true`、`"rules": 12`、`"hooks": 13` 和 `hook runner tests passed` 即可。

## 切换版本

安装脚本始终回到当前版本。仅在复现旧行为时手动切换。

```bash
find "$HOME/.gemini/config/agy-focus/versions" \
  -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V

ln -sfn versions/v1.12.0 "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

以后运行 `bash scripts/install.sh` 会回到最新版。

## 删除

这会移除链接并把配置移到带时间戳的目录，不会立即删除该目录。

```bash
REMOVED_DIR="$HOME/.gemini-removed-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REMOVED_DIR/config"

if [ -L "$HOME/.gemini/GEMINI.md" ]; then unlink "$HOME/.gemini/GEMINI.md"; fi
if [ -L "$HOME/.gemini/config/hooks.json" ]; then unlink "$HOME/.gemini/config/hooks.json"; fi
if [ -L "$HOME/.gemini/config/skills" ]; then unlink "$HOME/.gemini/config/skills"; fi
if [ -e "$HOME/.gemini/config/agy-focus" ] || [ -L "$HOME/.gemini/config/agy-focus" ]; then
  mv "$HOME/.gemini/config/agy-focus" "$REMOVED_DIR/config/agy-focus"
fi

printf '%s\n' "$REMOVED_DIR"
```

确认输出路径后再删除：

```bash
rm -rf "$REMOVED_DIR"
```

## 恢复备份

填入安装脚本输出的实际路径。

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/config/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/config/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/config/skills" "$HOME/.gemini/config/skills"
```

## UI 规则

- 不写模糊的 AI 文案、空泛的未来口号、魔法棒图标、假指标或装饰性 3D 图。
- 不把紫蓝渐变、重复圆角卡片和无意义动画当成默认方案。
- 从真实任务、现有系统、信息层级和可访问性出发做界面。
- 改代码前读完安全的文本文件；搜索结果或几行内容不算完整阅读。

## 目录

- `agy-focus/versions/` — 版本化配置
- `agy-focus/current` — 当前配置链接
- `scripts/install.sh` — 更新、备份、安装、验证
- `installed/` — 当前安装表面的副本

## 帮助与贡献

- [Support](../SUPPORT.md)
- [Security](../SECURITY.md)
- [Contributing](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)

MIT 许可证。请查看 [LICENSE](../LICENSE)。
