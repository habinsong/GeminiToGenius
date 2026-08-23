# GeminiToGenius

> Gemini を少しでもマシにするためのハーネスです。

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Antigravity と Antigravity IDE の Gemini 3.7 Flash (High) 向けグローバルルール・フック・スキルです。

## 初回インストール

macOS では次の 1 行を実行します。

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

スクリプトは `git pull --ff-only`、既存プロファイルの日時付きバックアップ、現在プロファイル(v2.12.0)のインストール、検証の順に実行します。

`curl | sh` は使いません。clone 後にローカルのスクリプトを実行します。必要なコマンドは `git`、`python3`、`rsync` です。`/GTG` の UI 検証にはインストール済みの Google Chrome または Chromium も必要です。`Installed agy-focus v2.12.0` が出たら Antigravity または Antigravity IDE を再起動します。

## 内容

| 項目 | 現在値 (v2.12.0) |
| --- | --- |
| 対象モデル | Gemini 3.7 Flash (High) ハイブリッド推論 |
| グローバルエンジニアリングルール | 22 完全ルール (GEMINI.md 100% 移植) |
| アーキテクチャ制限 | 500行制限ルール (500-Line Limit Rule) |
| デバッグパイプライン | 7段階デバッグ & 4大必須報告フォーマット |
| UI/UX デザインシステム | Windows 11 & WinUI 3 Fluent Design System 2.0 |
| ライフサイクルフック | 14 |
| 集中スキル | 11 |
| 外部プラグイン | なし |
| MCP | 接続自体がタスクの目的である場合のみ |

通常の依頼は自動で振り分けます。リポジトリや UI を厳格モードで扱う場合は `/GTG` で始めます。

```text
/GTG "habinsong/GeminiToGenius" を説明するWebページを作成して
```

## UI・実装ルール

- **Zero AI Slop**: 曖昧な AI コピー、魔法の杖アイコン、偽の指標、装飾用 3D を徹底排除。
- **Windows 11 & WinUI 3**: Mica/Acrylic サーフェス、Settings Cards、ToggleSwitch、Windows Terminal。
- **500行制限ルール (500-Line Limit Rule)**: 単一ファイル 500 行を超えず、SRP に基づくモジュール分割を義務化。
- **フルビューコード読取**: 1行目から最後まで連続読取。断片 snippet や幻覚を禁止。
- **Chrome 3段階描画計測**: `verify_ui_render.py` で 320px・768px・1280px の横切れゼロを検証。
- **5大標準応答フォーマット**: 変更概要・修正ファイル・実行コマンド・検証結果・残存リスクで報告。

## ヘルプと貢献

- [Support](../SUPPORT.md)
- [Security](../SECURITY.md)
- [Contributing](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)

MIT ライセンスです。[LICENSE](../LICENSE) を確認してください。
