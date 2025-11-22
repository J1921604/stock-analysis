
# 東京電力・中部電力・JERA 経営ダッシュボード — 仕様書

> ファイル名案: `tokyo_chubu_jera_dashboard_spec.md`

---

## 1. 目的
- 東京電力（TEPCO）、中部電力（Chubu）、JERA の経営状況（財務・業績・株価・主要KPI）を一元的に集約・可視化するWebダッシュボードを実装するための仕様書。
- データはすべて**SQLite**1ファイルで管理し、**GitHub Actions** の日次バッチで更新、リポジトリをストレージ兼配布源として利用する。フロントエンドは静的HTML＋JavaScript（GitHub Pages）で動作し、ブラウザが最新のSQLiteを取得して解析・表示する。

## 2. スコープ
- 対象企業: 東京電力（東京電力ホールディングス）、中部電力、JERA。
- 収集対象データ:
  - 連結/個別財務諸表（貸借対照表、損益計算書、キャッシュフロー計算書）
  - 四半期/通期決算報告（決算短信、決算説明資料PDF）
  - 株価・時系列（終値、始値、高値、安値、出来高）
  - 有価証券報告書の主要指標（ROE、ROA、営業利益率等）
  - 発電量・燃料費・燃料構成（公開データがある場合）
  - 債務・格付け、資本政策（増資・資本コスト）
  - ニュースやIRのテキスト要約（任意）

## 3. 要求非機能要件
- 最低限のインフラ: GitHub リポジトリのみ。
- 更新頻度: 日次（JST 18:00 に cron で実行）。
- データの一貫性: バッチは**インクリメンタル更新**（SQLite内の最新日付以降のみ上書き/追加）で実行。
- フロントエンドはオフライン/ローカルDB指定で動作可能。
- セキュリティ: 公開リポジトリの場合、機密情報（APIキー等）は GitHub Secrets に格納。SQLite公開は意図的に許可された範囲のみ。

## 4. 全体アーキテクチャ（概観）
1. GitHub リポジトリ
   - `data/`：生データファイル（CSV/JSON/PDF）を保存（raw sync）。
   - `db/`：最新版 `dashboard.sqlite` を格納。
   - `src/`：フロントエンド静的ファイル（HTML/CSS/JS）
   - `.github/workflows/`：GitHub Actions ワークフロー
   - `scripts/`：データ取得・解析用スクリプト（Python/Node）

2. GitHub Actions（cron で日次実行）
   - ステップ:
     1. リポジトリをチェックアウト
     2. `db/dashboard.sqlite` をダウンロード（存在すれば）
     3. 各データソースから当日以降の差分データをダウンロード
     4. ダウンロードデータをパース・正規化
     5. `dashboard.sqlite` にインクリメンタルで追記（トランザクション管理）
     6. 生データのバックアップを `data/raw/YYYY-MM-DD/` に sync
     7. 解析処理（指標更新、アラート判定）を実行
     8. 必要なら GitHub Issue を作成して通知
     9. `db/dashboard.sqlite` をコミットしてプッシュ（overwrite）
    10. presigned URL を生成して解析ページ（GitHub Pages）に反映するためのクエリパラメータ用URLを作成

3. フロントエンド（静的）
   - ブラウザが起動時に `db/dashboard.sqlite` をダウンロード（クエリに presigned URL が含まれる）
   - `sql.js` / `sqlite-wasm` を利用してブラウザ上で直接SQL実行
   - 各社カード（Company Card）ごとに指標・グラフ・解説を表示
   - ユーザーによりローカルSQLiteを選択可能（ファイル入力）

## 5. データモデル（SQLite スキーマ案）
- `companies` (企業基本情報)
  - `company_id` TEXT PRIMARY KEY
  - `name` TEXT
  - `ticker` TEXT
  - `exchange` TEXT
  - `sector` TEXT
  - `source_url` TEXT

- `raw_files` (取得した生データのメタ)
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `company_id` TEXT
  - `file_path` TEXT
  - `file_type` TEXT
  - `fetched_at` DATETIME

- `financial_statements` (時系列の主要財務)
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `company_id` TEXT
  - `report_date` DATE  -- 決算日または集計日
  - `period_type` TEXT -- e.g. FY, Q1, Q2
  - `total_assets` REAL
  - `total_liabilities` REAL
  - `equity` REAL
  - `revenue` REAL
  - `operating_income` REAL
  - `net_income` REAL
  - `cash_and_equivalents` REAL
  - `long_term_debt` REAL
  - `currency` TEXT
  - `source_file_id` INTEGER

- `stock_prices` (日次株価)
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `company_id` TEXT
  - `date` DATE
  - `open` REAL
  - `high` REAL
  - `low` REAL
  - `close` REAL
  - `volume` INTEGER
  - `adjusted_close` REAL

- `kpis` (計算された指標の時系列)
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `company_id` TEXT
  - `date` DATE
  - `metric` TEXT -- e.g. ROE, ROA, EBITDA_MARGIN
  - `value` REAL

- `alerts` (解析で生成した通知)
  - `id` INTEGER PRIMARY KEY AUTOINCREMENT
  - `created_at` DATETIME
  - `company_id` TEXT
  - `type` TEXT
  - `severity` TEXT
  - `message` TEXT
  - `payload` TEXT

※ インデックスは `company_id, date/report_date` に対して設定する。

## 6. 取得すべき指標（推奨）
### 財務系
- 売上高（Revenue）
- 営業利益（Operating Income）
- 営業利益率
- 経常利益
- 当期純利益（Net Income）
- 総資産／自己資本（Total Assets / Equity）
- 自己資本比率
- 有利子負債（短期+長期）
- ネットキャッシュ（現金同等物 − 有利子負債）
- FCFF/FCFE（可能なら）

### 収益性・効率性指標
- ROE, ROA
- EBITDA マージン
- 売上高成長率（YoY / QoQ）
- 在庫回転率（該当する事業で）

### 市場・株式指標
- 時価総額
- P/E, EV/EBITDA
- 株価の単純移動平均（MA 20, 50, 200）
- ボラティリティ（過去30日など）

### 電力業界固有指標（可能なら）
- 発電量（GWh）／発電構成（火力・原子力・再エネ割合）
- 燃料費（燃料費調整額）
- 燃料構成別コスト
- FIT/再エネ関連収益やリスク
- 燃料在庫（日数換算）

### リスク指標
- 債務償還年数（長期負債 / EBITDA）
- 金利支払負担（利息費用 / 営業利益）
- 格付け変動（外部データ）

## 7. データソース候補（自動取得可能なもの）
- 各社IRサイト（決算短信PDF、決算説明資料、IRライブラリ）
- EDINET / TDnet（日本のディスクロージャ）
- Yahoo Finance / Alpha Vantage / IEX / Google Finance（株価）
- Bloomberg/Reuters（有料; 利用可能なら）
- 経産省・電力広域的運営推進機関等の公開発電データ
- 格付機関・証券会社レポート（Webスクレイピング対象）
- 既存CSV/Excel（証券会社提供、社内データ）

## 8. データ取得パイプライン（詳細）
### 8.1. GitHub Actions ワークフロー（概略）
- イベント: `schedule` + `workflow_dispatch`
- 実行環境: `ubuntu-latest`
- ステップ:
  1. checkout
  2. setup Python/Node
  3. (任意) キャッシュ依存ライブラリ
  4. `scripts/fetch_metadata.py` を実行して最新rawファイルリストを取得
  5. `scripts/fetch_and_parse.py --since <latest_date_in_db>` を実行
  6. `scripts/append_to_sqlite.py db/dashboard.sqlite` を実行
  7. `scripts/run_analysis.py`（指標計算・アラート生成）
  8. `scripts/sync_raw.sh`（rawを `data/raw/YYYY-MM-DD/` に保存）
  9. commit & push `db/dashboard.sqlite` と `data/raw` のメタ
  10. create GitHub Issue あるいは dispatch notification

### 8.2. インクリメンタル更新戦略
- 各データソースごとに最新日を判定（`SELECT MAX(date) FROM stock_prices WHERE company_id = ?` 等）
- 取得スクリプトは `--since` パラメータを受け取り、その日付以降のみダウンロード
- PDF→テキスト抽出は可変（PDF OCR が必要な場合は外部サービスや Tesseract を利用）

### 8.3. ログ・リトライ
- 失敗時は明確なエラーコードを残し、部分成功を担保
- 重要ステップはリトライ（exponential backoff）
- 最終的なSQLiteアップロードは全ステップ成功時にのみ行う（トランザクション）

## 9. フロントエンド設計（カード構成）
- 概要ページ（Summary）: 各社カードをグリッド表示。主要KPIのスナップショット、直近のアラート、SQLiteダウンロードリンク、解析ページリンク。
- 企業カード（Company Card）:
  - ヘッダー：社名、ティッカー、時価総額、最新株価
  - KPI行：ROE, 営業利益率, 自己資本比率, 有利子負債/EBITDA
  - グラフ領域：売上高推移、営業利益推移、株価推移（インタラクティブ）
  - 解説エリア：AIによる短い要約（直近決算のポイント）、注目指標の解説
  - ダウンロード：該当企業の原本ファイル、該当期間のCSV、クエリパラメータ付きSQLiteダウンロードリンク

- 詳細ページ（Company Details）: 時系列表、エクスポート機能、カスタム指標の計算UI
- グラフ実装: Chart.js / Recharts / D3（静的配布の簡便さ重視でChart.js推奨）
- SQLite in browser: `sql.js`（WebAssembly）推奨。大きなDBに対してはレンジを絞るクエリ設計。

## 10. 解析・アラート設計
- 定義済みルール例:
  - 営業利益率が過去4四半期平均より 30% 低下 => 重大アラート
  - ネットキャッシュがマイナスで、負債比率が上昇 => 注視
  - 株価がMA(50) を 10% 下回る & 出来高増加 => 市場異常アラート
- アラート出力: `alerts` テーブルへ保存 + GitHub Issue 作成（重要度によってIssueラベルを変える）

## 11. 通知・運用
- GitHub Issue: 日次バッチ内で `gh` CLI または GitHub API を用いてIssueを作成。タイトルに `[ALERT]` を付与。
- メール: リポジトリオーナーにメール（GitHubのIssue通知 or external SMTP を利用）。
- ログ: Actions のログ + `logs/` に詳細ログを残す。

## 12. 開発・デプロイ手順（チェックリスト）
1. リポジトリ初期化（ブランチ保護/Secrets登録）
2. `scripts/` の雛形作成
3. SQLite スキーマ作成スクリプト
4. 一次データ取得スクリプト（東京電力・中部電力・JERA の公開IRから）
5. GitHub Actions ワークフロー実装（cron, secrets）
6. フロントエンド雛形（Summary, CompanyCard）
7. CI テスト（ローカルでの `scripts` 実行 → DB 更新 → フロントで確認）
8. GitHub Pages にデプロイ

## 13. サンプル GitHub Actions ワークフロー（抜粋）
```yaml
name: daily-update
on:
  schedule:
    - cron: "0 9 * * *" # Run daily at 6:00 PM JST (9:00 AM UTC)
  workflow_dispatch: {}
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install -r scripts/requirements.txt
      - name: Run fetch + append
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/fetch_and_parse.py --since $(python scripts/get_latest_date.py db/dashboard.sqlite)
          python scripts/append_to_sqlite.py db/dashboard.sqlite
          python scripts/run_analysis.py db/dashboard.sqlite
      - name: Commit DB
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add db/dashboard.sqlite data/raw/* || true
          git commit -m "daily data update: $(date -u +%Y-%m-%d)" || echo "no changes"
          git push
      - name: Create Issue on Alerts
        run: python scripts/create_github_issue_if_alerts.py db/dashboard.sqlite
```

## 14. 保守・拡張計画
- 将来的に対象企業・指標を追加しやすいモジュール設計（plugins/ 方式）
- データソースの障害時フォールバック（キャッシュ or サードパーティAPI）
- 有料API導入時の切替設定（機能フラグ）

## 15. セキュリティ注意点
- 機密情報（APIキー等）は GitHub Secrets に登録
- 公開リポジトリであれば、公開して良い範囲のデータのみ配布
- presigned URL は短期有効にする（1時間など）
- DB内の PII を取り扱わない

## 16. 必要作業（短期優先タスク）
1. SQLite スキーマと初期DBを作成
2. 各社のIR/TDnet/EDINETのスクレイピング仕様を作成
3. 株価データ取得スクリプト（Yahoo Finance 等）を作成
4. GitHub Actions ワークフローをセットアップ
5. フロントエンドの最低限のSummaryページを作る

---

### 付録: 提案 — 有用な追加機能
- AI 要約機能: 決算短信PDFを要約してカード内に短い解説を自動生成
- 比較ビュー: 3社を並べて同一指標で比較（相対評価）
- シナリオ分析: 燃料価格変動シナリオによる利益感応度分析
- パーソナライズド・アラート: 条件をユーザーがUIで設定可能

---


