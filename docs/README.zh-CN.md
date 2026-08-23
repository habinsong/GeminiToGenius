# GeminiToGenius

> 让 Gemini 更聪明好用的工程控制线束。

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

适用于 Antigravity 和 Antigravity IDE 中 Gemini 3.7 Flash (High) 的全局规则、钩子和技能集合。

## 首次安装

macOS 系统中只需运行一行命令：

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

脚本会按以下顺序执行：

1. 使用 `git pull --ff-only` 更新本地仓库
2. 将现有配置备份到带时间戳的文件夹
3. 安装当前配置文件 (v2.13.0)
4. 运行配置文件和钩子测试

不使用 `curl | sh`。依赖命令：`git`、`python3`、`rsync`。`/GTG` UI 验证需要已安装的 Google Chrome 或 Chromium。看到 `Installed agy-focus v2.13.0` 后重启 Antigravity 或 Antigravity IDE。

## 安装内容

| 项目 | 当前值 (v2.13.0) |
| --- | --- |
| 目标模型 | Gemini 3.7 Flash (High) 混合推理 |
| 全局工程规则 | 22 条完整规则 (GEMINI.md 100% 映射) |
| 架构防线 | 500 行限制规则 (500-Line Limit Rule) |
| 调试管线 | 7 步调试法 & 4 字段报告格式 |
| UI/UX 质量标准 | 任务导向 & Zero AI Slop UI 验证 |
| 生命周期钩子 | 14 |
| 专项技能 | 11 |
| 外部插件 | 无 |
| MCP | 仅在连接本身为任务目标时使用 |

普通请求会自动路由。严格模式请以 `/GTG` 开头。

## UI 与实现规则

- **Zero AI Slop**: 杜绝空洞 AI 文案、魔法棒图标、虚假指标和装饰性 3D 图形。
- **基于产品证据的 UI**: 界面完全基于真实产品需求与用户任务构建。
- **通俗易懂的人工文案**: 严禁生硬短语，使用自然完整的句子陈述，非技术人员也能轻松理解。
- **500 行限制规则 (500-Line Limit Rule)**: 单文件不超过 500 行，基于单一职责原则 (SRP) 拆分子模块。
- **全景代码阅读**: 必须从第 1 行完整阅读至末尾，严禁局部片段猜测或幻觉。
- **Chrome 三档视口测量**: `verify_ui_render.py` 验证 320px、768px、1280px 零水平溢出。
- **5 大标准响应格式**: 变更摘要、修改文件、执行命令、验证结果、剩余风险。

## 帮助与贡献

- [Support](../SUPPORT.md)
- [Security](../SECURITY.md)
- [Contributing](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)

MIT 协议，请参阅 [LICENSE](../LICENSE)。
