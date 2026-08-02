# GeminiToGenius

> Gemini を少しでもマシにするためのハーネスです。

[English](../README.md) · [한국어](README.ko.md) · [日本語](README.ja.md) · [简体中文](README.zh-CN.md)

Antigravity と Antigravity IDE の Gemini 3.6 Flash (High) 向けグローバルルール・フック・スキルです。

## 初回インストール

macOS では次の 1 行を実行します。

```bash
git clone https://github.com/habinsong/GeminiToGenius.git && bash GeminiToGenius/scripts/install.sh
```

スクリプトは `git pull --ff-only`、既存プロファイルの日時付きバックアップ、現在プロファイルのインストール、検証の順に実行します。

`curl | sh` は使いません。clone 後にローカルのスクリプトを実行します。必要なコマンドは `git`、`python3`、`rsync` です。`/GTG` の UI 検証にはインストール済みの Google Chrome または Chromium も必要です。`Installed agy-focus v...` が出たら Antigravity または Antigravity IDE を再起動します。

## 内容

| 項目 | 現在値 |
| --- | --- |
| 対象モデル | Gemini 3.6 Flash (High) |
| 常時ルール | 12 |
| ライフサイクルフック | 14 |
| 集中スキル | 11 |
| 外部プラグイン | なし |
| MCP | 接続自体がタスクの目的である場合のみ |

通常の依頼は自動で振り分けます。リポジトリや UI を厳格モードで扱う場合は `/GTG` で始めます。

```text
/GTG "habinsong/GeminiToGenius" 를 설명하는 웹페이지 만들어줘
```

`/GTG` は、ソース優先の調査、ファイル全体の読取、一次資料、UI ソース書込前の計画、公式 UI 資料4件・3ホスト・4分野、Webページ・ランディング・静的ページの2経路以上、320px・768px・デスクトップのブラウザ描画、描画後の Computer Use/vision 観察、観察後の公式 Web 比較、計画と実装の照合、書込後検証を依頼の終了まで維持します。

## `GEMINI.md` を常時使う理由

- Antigravity は `~/.gemini/GEMINI.md` を[グローバルルール](https://antigravity.google/docs/ide/rules)として読み込みます。
- v2.10.0 のエントリポイントは 5,982 文字です。ソース優先ルーティング、連続ファイルインテーク、判断台帳の計画、復旧経路の確認、描画→vision→Web 比較の UI 監査ゲートだけを置きます。
- コード、アーキテクチャ、UI、コピー、調査の手順は必要な作業でのみ[集中スキル](https://antigravity.google/docs/skills?app=antigravity-ide)として読み込みます。
- [フック](https://antigravity.google/docs/hooks)が高リスク境界を検査するため、全手順を毎回のプロンプトへ入れません。
- 無関係なリポジトリ履歴やタスク固有文書は既定で注入しません。

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

`"ok": true`、`"rules": 12`、`"hooks": 14`、`"skills": 11`、`hook runner tests passed` が出れば完了です。描画後は各経路・状態を Computer Use/vision で確認し、`search_web` と公式 `read_url_content` で比較します。

## バージョン変更

現在版も過去版もインストーラで切り替えます。更新 → バックアップ → インストール → 検証の順序は同じです。

```bash
bash scripts/install.sh --version v2.10.0
bash scripts/install.sh --help
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

## UI・実装ルール

- IDE-native `analyze`・`inspect`・`explore` で README・docs・workspace フォルダー・ファイルツリーを先に分析する経路も、同じソースインテークゲートでブロックします。ディレクトリ要約はソース読了として数えません。
- フック payload に届く未登録の分析・探索ツールも、ソースインテーク前は拒否します。明示的な経路は `view_file` と登録済みの検証コマンドです。

- 曖昧な AI コピー、未来を語るだけの文、魔法の杖アイコン、偽の指標・ダッシュボード、装飾用 3D を入れません。
- 紫青の既定グラデーション、ガラス・グロー、入れ子の丸カード、同じ余白・角丸の反復、理由のないアニメーションを入れません。
- 実際の製品、ユーザーの作業、データ、状態、情報階層、既存デザインシステム、アクセシビリティを根拠にします。
- モバイルファースト、320 CSS px のリフロー、見えるフォーカス、動きの軽減設定、測定済みの性能根拠を確認します。
- 同梱の `verify_ui_render.py` は、インストール済み Chrome で 320px・768px・1280px の横方向の切れを計測し、各幅の画像を作ります。Playwright は追加しません。
- `/GTG` の UI ソース書込前に `docs/plans/` の設計・実装・検証計画を作り、`verify_plan.py --require-multi-page --require-ui-evidence` を実行します。Webページ・ランディング・静的ページは既定で2経路以上に分け、`verify_multi_page.py` ですべてのページを確認します。
- UI 方向は公式資料4つ以上を3ホスト・4分野で照合し、evidence matrix に発見・決定・実装への影響・検証条件を残します。
- 描画後は各経路・状態を Computer Use/vision で確認し、その後 `search_web` と公式 `read_url_content` で画面判断を再照合します。
- リポジトリ全体の構造を把握してから、影響範囲の実装、呼び出し経路、状態・データ経路、テストを最後まで読みます。README と検索断片は実装根拠にしません。`cat`、`sed`、`rg`、`find`、`ls`、`tree`、`fd`、`git show`、`git ls-files` などの shell による読み取り・一覧化はソース確認が終わるまでブロックし、最後の検証は実際の成功結果がある場合だけ認めます。
- `/GTG` の読取・レビュー・診断でも `Stop` 時に実装ソースと関連テスト全体の読了を確認します。変更しないことを理由に README・docs だけを読んで完了する経路は許可しません。
- 別の GitHub リポジトリを説明する場合は、README・概要に加えて、インストールスクリプト、manifest、実ソースのいずれかを直接読みます。検索要約は根拠にしません。
- UI 状態、ドメイン判断、I/O、永続化、外部プロセスを一つの God Object に集めません。

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
