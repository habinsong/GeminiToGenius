# GeminiToGenius

> 一套让 Gemini 没那么笨的约束。

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

面向 Antigravity 和 Antigravity IDE 中 Gemini 3.6 Flash (High) 的全局规则、钩子和技能。

## 首次安装

macOS 上执行这一行：

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

脚本按顺序执行：`git pull --ff-only`、把现有配置移到带时间戳的备份目录、安装当前配置、运行验证。

不使用 `curl | sh`。先 clone，再运行本地脚本。需要 `git`、`python3` 和 `rsync`。`/GTG` UI 验证还需要已安装的 Google Chrome 或 Chromium。出现 `Installed agy-focus v...` 后重启 Antigravity 或 Antigravity IDE。

## 内容

| 项目 | 当前值 |
| --- | --- |
| 目标模型 | Gemini 3.6 Flash (High) |
| 常驻规则 | 12 |
| 生命周期钩子 | 14 |
| 聚焦技能 | 11 |
| 外部插件 | 无 |
| MCP | 仅当连接本身就是任务目标 |

普通请求会自动路由。仓库或 UI 工作需要严格模式时，以 `/GTG` 开头。

```text
/GTG "habinsong/GeminiToGenius" 를 설명하는 웹페이지 만들어줘
```

`/GTG` 会在整个请求中保持源码优先、完整文件读取、第一方仓库证据、UI 源码写入前的计划、必要时的多页面路由、320px、768px 与桌面浏览器渲染、写入后验证。

## 为什么始终保留 `GEMINI.md`

- Antigravity 把 `~/.gemini/GEMINI.md` 作为[全局规则](https://antigravity.google/docs/ide/rules)加载。
- v2.4.0 入口为 5,316 个字符，仅保留路由、安全、证据、计划、完成和 UI 审计门槛。
- 代码、架构、UI、文案和检索流程只在相关任务中作为[聚焦技能](https://antigravity.google/docs/skills?app=antigravity-ide)加载。
- [钩子](https://antigravity.google/docs/hooks)检查高风险边界，不必把全部流程塞进每次提示。
- 默认不注入无关的仓库历史和任务文档。

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

看到 `"ok": true`、`"rules": 12`、`"hooks": 14`、`"skills": 11` 和 `hook runner tests passed` 即可。

## 切换版本

当前版本和历史版本都通过安装脚本切换。更新 → 备份 → 安装 → 验证的顺序不变。

```bash
bash scripts/install.sh --version v2.4.0
bash scripts/install.sh --help
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

## UI 与实现规则

- 使用 IDE 原生 `analyze`、`inspect`、`explore` 先分析 README/docs 的路径也会被同一个源代码优先门禁拦截。

- 不写模糊的 AI 文案、空泛的未来口号、魔法棒图标、假指标与假仪表盘，也不用装饰性 3D 图。
- 不把紫蓝渐变、玻璃与辉光、嵌套圆角卡片、相同间距与圆角的重复、无意义动画当成默认方案。
- 以真实产品、用户任务、数据、状态、信息层级、现有设计系统和可访问性为依据。
- 检查移动优先、320 CSS px 回流、可见焦点、减少动态效果设置和经过测量的性能依据。
- 内置 `verify_ui_render.py` 使用已安装的 Chrome 测量 320px、768px、1280px 横向裁切并生成各视口截图，不安装 Playwright。
- `/GTG` UI 源码变更前先写 `docs/plans/` 的设计、实现和验证计划并运行 `verify_plan.py`。存在多个页面时，用 `verify_multi_page.py` 渲染并检查所有路径。
- 先掌握整个仓库结构，再完整阅读影响范围内的实现、调用路径、状态与数据路径、测试。README 和搜索片段不算实现证据。源代码检查完成前，`cat`、`sed`、`rg`、`git show` 等 shell Markdown 读取会被拦截；最后的验证还必须有真实的成功结果。
- 说明其他 GitHub 仓库时，除 README 或仓库概览外，还要直接读取安装脚本、manifest 或实际源码之一。搜索摘要不算证据。
- 不把 UI 状态、领域决策、I/O、持久化和外部进程塞进一个 God Object。

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
