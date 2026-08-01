# GeminiToGenius

Antigravity と Antigravity IDE で Gemini 3.6 Flash (High) を使うための、バージョン管理された集中維持ハーネスです。

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

現在の指示、アクティブな作業ウィンドウ、関連ファイル、検証可能な結果にだけ集中するためのルールと実行境界を管理します。

## 構成

- 常時注入する指示ファイル 12 個
- ライフサイクルフック 8 個
- 集中維持スキル 4 個
- `v1.0.0` から `v1.14.2` までのバージョン履歴
- 外部プラグインなし
- MCP は接続が必要なタスクでのみ使用

## 目的

常時注入する指示が長いと、途中で切れたり効きが弱くなります。ルールを短いファイルに分け、1 つのエントリポイントを生成し、変更をすべてバージョン管理します。

## 対応環境

| 対象 | 対応プロファイル |
| --- | --- |
| Antigravity | グローバル `~/.gemini/GEMINI.md` と `~/.gemini/config/` |
| Antigravity IDE | グローバル `~/.gemini/GEMINI.md` と `~/.gemini/config/` |
| モデル | `Gemini 3.6 Flash (High)` |

## インストール

macOS 向けです。順番は `clone → update → backup → install → verify` です。リポジトリの更新をバックアップより先に完了してください。

```bash
git clone https://github.com/habinsong/GeminiToGenius.git
cd GeminiToGenius
```

新しく clone した直後は最新状態です。既存の clone を使う場合だけ更新します。

```bash
cd GeminiToGenius && git pull --ff-only
```

プロファイルを上書きする前にバックアップします。

```bash
BACKUP_DIR="$HOME/.gemini-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR" "$HOME/.gemini/config"
if [ -e "$HOME/.gemini/config/agy-focus" ] || [ -L "$HOME/.gemini/config/agy-focus" ]; then mv "$HOME/.gemini/config/agy-focus" "$BACKUP_DIR/agy-focus"; fi
if [ -e "$HOME/.gemini/GEMINI.md" ] || [ -L "$HOME/.gemini/GEMINI.md" ]; then mv "$HOME/.gemini/GEMINI.md" "$BACKUP_DIR/GEMINI.md"; fi
if [ -e "$HOME/.gemini/config/hooks.json" ] || [ -L "$HOME/.gemini/config/hooks.json" ]; then mv "$HOME/.gemini/config/hooks.json" "$BACKUP_DIR/hooks.json"; fi
if [ -e "$HOME/.gemini/config/skills" ] || [ -L "$HOME/.gemini/config/skills" ]; then mv "$HOME/.gemini/config/skills" "$BACKUP_DIR/skills"; fi
printf '%s\n' "$BACKUP_DIR"
```

最後に表示されたパスが復元ポイントです。バックアップ後にプロファイルを入れます。

```bash
cp -a agy-focus "$HOME/.gemini/config/agy-focus"
ln -sfn versions/v1.14.2 "$HOME/.gemini/config/agy-focus/current"
ln -sfn config/agy-focus/current/GEMINI.md "$HOME/.gemini/GEMINI.md"
ln -sfn agy-focus/current/hooks/hooks.json "$HOME/.gemini/config/hooks.json"
ln -sfn agy-focus/current/skills "$HOME/.gemini/config/skills"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

確認値は `"ok": true`、`"rules": 12`、`"hooks": 8`、`"target": "Gemini 3.6 Flash (High)"` です。インストール後に Antigravity または Antigravity IDE を再起動します。

## 更新

```bash
cd GeminiToGenius && git pull --ff-only
```

その後、バックアップから検証までをもう一度実行します。プロファイルを置き換える前にバックアップを取ります。

## バージョン変更

```bash
find "$HOME/.gemini/config/agy-focus/versions" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V
ln -sfn versions/v1.12.0 "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

## 削除と復元

```bash
REMOVED_DIR="$HOME/.gemini-removed-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$REMOVED_DIR"
if [ -L "$HOME/.gemini/GEMINI.md" ]; then unlink "$HOME/.gemini/GEMINI.md"; fi
if [ -L "$HOME/.gemini/config/hooks.json" ]; then unlink "$HOME/.gemini/config/hooks.json"; fi
if [ -L "$HOME/.gemini/config/skills" ]; then unlink "$HOME/.gemini/config/skills"; fi
if [ -d "$HOME/.gemini/config/agy-focus" ]; then mv "$HOME/.gemini/config/agy-focus" "$REMOVED_DIR/agy-focus"; fi
printf '%s\n' "$REMOVED_DIR"
```

表示されたパスを確認してから完全に削除します。

```bash
rm -rf "$REMOVED_DIR"
```

バックアップの復元:

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/skills" "$HOME/.gemini/config/skills"
```

## UI ルール

- AI Slop の文言、曖昧な見出し、抽象的な魔法の杖アイコンを使わない
- 目的のないホバー効果とマイクロインタラクションを使わない
- 丸いカードの反復と機械的な対称レイアウトを使わない
- `Inter` と `Roboto` を習慣で使わない
- 紫から青へのネオングラデーションを既定解にしない
- intrinsic sizing、fluid typography、非対称配置、モバイル優先を先に検討する

## ライセンス

MIT ライセンスです。[LICENSE](../LICENSE) を確認してください。
