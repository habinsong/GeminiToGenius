# GeminiToGenius

> Gemini が実作業でだんだん頼りなくなったので作りました。Gemini を少しでもマシにするためのハーネスです。

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Antigravity と Antigravity IDE の Gemini 3.6 Flash (High) 向けグローバルルール・フック・スキルです。

## 初回インストール

macOS では次の 1 行を実行します。

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

スクリプトは `git pull --ff-only`、既存プロファイルの日時付きバックアップ、現在プロファイルのインストール、検証の順に実行します。

`curl | sh` は使いません。clone 後にローカルのスクリプトを実行します。必要なコマンドは `git`、`python3`、`rsync` です。`Installed agy-focus v...` が出たら Antigravity または Antigravity IDE を再起動します。

## 内容

| 項目 | 現在値 |
| --- | --- |
| 対象モデル | Gemini 3.6 Flash (High) |
| 常時ルール | 12 |
| ライフサイクルフック | 13 |
| 自動スキル | 8 |
| 外部プラグイン | なし |
| MCP | 接続自体がタスクの目的である場合のみ |

通常の自然言語で自動動作します。`/` や `@` は不要です。

## 既存ユーザーの更新

古い clone では同じスクリプトを実行します。

```bash
cd /path/to/GeminiToGenius
bash scripts/install.sh
```

先に checkout を更新するため、古いインストールも現在プロファイルに切り替わります。tracked 変更がある場合は `git pull` 前に停止します。commit、stash、または整理を先に行ってください。

実行ごとに次のようなバックアップパスが表示されます。

```text
/Users/you/.gemini-backup-YYYYMMDD-HHMMSS
```

## 検証

```bash
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/test_hook_runner.py"
```

`"ok": true`、`"rules": 12`、`"hooks": 13`、`hook runner tests passed` が出れば完了です。

## バージョン変更

インストーラは常に現在バージョンに戻します。古い動作を再現する場合だけ手動で切り替えます。

```bash
find "$HOME/.gemini/config/agy-focus/versions" \
  -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort -V

ln -sfn versions/v1.12.0 "$HOME/.gemini/config/agy-focus/current"
python3 "$HOME/.gemini/config/agy-focus/current/scripts/verify_profile.py"
```

後で `bash scripts/install.sh` を実行すれば最新に戻ります。

## 削除

リンクを外し、プロファイルを日時付きフォルダへ移動します。フォルダ自体は消しません。

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

表示されたパスを確認してから削除します。

```bash
rm -rf "$REMOVED_DIR"
```

## バックアップの復元

インストーラが出力した実際のパスを指定します。

```bash
BACKUP_DIR="$HOME/.gemini-backup-YYYYMMDD-HHMMSS"
mv "$BACKUP_DIR/config/agy-focus" "$HOME/.gemini/config/agy-focus"
mv "$BACKUP_DIR/GEMINI.md" "$HOME/.gemini/GEMINI.md"
mv "$BACKUP_DIR/config/hooks.json" "$HOME/.gemini/config/hooks.json"
mv "$BACKUP_DIR/config/skills" "$HOME/.gemini/config/skills"
```

## UI ルール

- 曖昧な AI コピー、未来を語るだけの文、魔法の杖アイコン、偽の指標、装飾用 3D を入れません。
- 紫青の既定グラデーション、丸いカードの反復、理由のないアニメーションを入れません。
- 実際の作業、既存システム、情報の優先順位、アクセシビリティから画面を作ります。
- コード変更前に安全なテキストファイルをすべて読みます。検索結果や数行だけでは不十分です。

## 構成

- `agy-focus/versions/` — バージョン別プロファイル
- `agy-focus/current` — 現在プロファイルへのリンク
- `scripts/install.sh` — 更新・バックアップ・インストール・検証
- `installed/` — 現在のインストール表面のコピー

## ヘルプと貢献

- [Support](../SUPPORT.md)
- [Security](../SECURITY.md)
- [Contributing](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)

MIT ライセンスです。[LICENSE](../LICENSE) を確認してください。
