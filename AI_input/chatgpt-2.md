
# AI株式分析システム 仕様書（完全再現用・詳細版）

---

## 目次 (TOC)
1. システム概要
2. 機能要件（完全版）
3. 非機能要件
4. アーキテクチャ分解
5. 日次バッチ処理仕様（GitHub Actionsワークフロー）
6. SQLite スキーマ（逆算／完全DDL）
7. S3 保存戦略／ライフサイクル
8. ブラウザ内解析ロジックのフロー（1ファイルSPA）
9. 各ランキング算出ロジック（数式＆疑似コード）
10. 通知（GitHub Issue）仕様
11. CI/CD とデプロイ手順
12. セキュリティ／認証／権限設計
13. テスト計画（単体・統合・回帰）
14. 運用・監視・障害復旧
15. 他AIが再現するための最短手順（リプロデュースガイド）
16. 付録: サンプルコード・SQL・ワークフローYAML

---

# 1. システム概要（要約）
- データソース: EDINET (XBRL)、株価API/CSV、その他公表資料
- データ保管: SQLite 単一ファイル + S3 生データアーカイブ
- バッチ基盤: GitHub Actions（cron）
- 配信 UI: GitHub Pages の 1 ファイル HTML（sqlite-wasm + lightweight-charts）
- 通知: GitHub Issue 自動生成
- 目的: 個別株のスクリーニングと市場・銘柄可視化。自動検出された候補を人間が検討して売買判断を行う。

---

# 2. 機能要件（完全版）

## 2.1 ユーザー向け機能
- ランキング一覧（ネットネットバリュー、オニール成長株）
- 銘柄詳細ページ（財務指標・PBR推移・EPS推移・決算発表マーカー）
- マーケット天井検出ツール（分配日ベース）
- パラメータ調整UI（資産の割引率、スクリーニング閾値等）
- データダウンロード（presigned SQLite / gzip）
- ローカルDB選択（dev向け）

## 2.2 管理者／運用者向け機能
- GitHub Actions ログ確認
- S3オブジェクト管理（年毎 tar.gz）
- Issue による通知履歴・クローズ運用
- ワークフロー手動トリガー（workflow_dispatch）

## 2.3 データ要件
- 株価: 日次終値、出来高、始値、高値、安値（adjusted 有り）
- 財務: 決算日、売上高、営業利益、当期利益、有形固定資産、現金及び現金同等物、有価証券、負債項目（短期・長期）
- XBRLパース: タグマッピング（EDINETスキーマ→内部フィールド）
- 履歴: 少なくとも過去10年分を保持

## 2.4 エクスポート / インポート
- S3 に生データ sync（aws s3 sync）
- presigned URL は毎日更新（7日有効）

---

# 3. 非機能要件
- 可用性: GitHub Actions と S3 により 99% 可用を狙う
- 性能: ブラウザ解析は 5000 銘柄程度の表示・操作で滑らかに動作
- ストレージ: SQLite は数百 MB（gzip 併用）
- セキュリティ: presigned URL を採用して認証を最小化
- 保守性: ソースはGit管理、CIはGitHub Actions

---

# 4. アーキテクチャ分解

## 4.1 コンポーネント一覧
1. GitHub Actions ワークフロー（fetch, parse, import, analyze, upload, notify）
2. パースライブラリ（Pythonモジュール: fetcher、xbrl_parser、price_importer）
3. SQLite DB（スキーマ）
4. S3 バケット（raw/, db/）
5. GitHub Pages（1ファイルSPA）
6. Notification module（github_issue_creator）

## 4.2 各コンポーネントの責務
- fetcher: EDINET API と株価APIから指定日以降のファイルを差分取得
- xbrl_parser: XBRL の XML を読み、タグを内部スキーマに正規化して出力
- import_to_sqlite: 正規化されたCSV/JSONをSQLiteに upsert
- analyzer: SQLite上で指標を計算し、閾値を満たす銘柄を検出
- ui_generator: 解析結果を表示する静的HTML（の更新）
- s3_sync: 生データの同期とDBのアップロード

---

# 5. 日次バッチ処理仕様（GitHub Actionsワークフロー）

## 5.1 ワークフロー目的
- 前回更新日以降の差分を取得し、DBを更新、解析、通知、アーティファクト公開

## 5.2 トリガー
- schedule: cron "0 9 * * *" (UTC 9 -> JST 18:00)
- workflow_dispatch: manual

## 5.3 環境 / シークレット
- AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
- S3_BUCKET
- GITHUB_TOKEN (Actions default)
- PRICE_API_KEY (もし外部株価API使用時)

## 5.4 ステップ（詳細）
1. checkout
2. setup-python (3.11)
3. install dependencies (`pip install -r requirements.txt`) — requirements: boto3, requests, pandas, lxml, sqlite-utils, numpy, scipy, scikit-optimize(optional)
4. `aws s3 cp s3://{bucket}/db/latest.sqlite ./` (retry logic 3回)
5. `python fetch_prices.py --since latest_date` (1秒/ファイル throttle)
6. `python fetch_xbrl.py --since latest_date`
7. `python parse_xbrl.py --input raw/xbrl --out normalized/` (出力: CSV/JSON)
8. `python import_to_sqlite.py --db latest.sqlite --input normalized/` (トランザクション単位で upsert)
9. `python analyze.py --db latest.sqlite --out results.json` (検出結果)
10. if results contains new_candidates: `python create_github_issue.py --payload results.json`
11. `aws s3 sync raw/ s3://{bucket}/raw/ --acl private` (圧縮して保存)
12. `aws s3 cp latest.sqlite s3://{bucket}/db/latest.sqlite --acl private` (gzip版も置く)
13. Generate presigned URL for latest.sqlite.gz (expiry 7 days) and write to Actions summary
14. Commit/push summary HTML update (if necessary) or upload static HTML to gh-pages branch

## 5.5 エラー処理
- 各ステップは retry (3 attempts) と exponential backoff
- 失敗時は workflow を fail-fast にせずに「該当処理以外は継続」するオプションあり（設定で切替）
- 重大（DB更新失敗/保存失敗）は Slack/email (オプション)へ通知

---

# 6. SQLite スキーマ（完全DDL）

以下はブログの機能要件から逆算したスキーマ。インデックス・制約含む。

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS companies (
  company_id TEXT PRIMARY KEY, -- EDINET/JPX共通の識別子（e.g., ticker or edinet_code）
  ticker TEXT,
  name TEXT,
  sector TEXT,
  industry TEXT,
  market TEXT,
  last_update DATE
);

CREATE TABLE IF NOT EXISTS stock_prices_daily (
  company_id TEXT,
  date DATE,
  open REAL,
  high REAL,
  low REAL,
  close REAL,
  adj_close REAL,
  volume INTEGER,
  PRIMARY KEY (company_id, date),
  FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

CREATE INDEX IF NOT EXISTS idx_prices_company_date ON stock_prices_daily(company_id, date DESC);

CREATE TABLE IF NOT EXISTS xbrl_raw (
  file_id TEXT PRIMARY KEY,
  company_id TEXT,
  filing_date DATE,
  report_type TEXT,
  raw_xml BLOB,
  s3_path TEXT,
  imported BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS xbrl_normalized (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT,
  report_date DATE,
  fiscal_year INTEGER,
  fiscal_period TEXT,
  tag TEXT,
  value REAL,
  unit TEXT,
  context TEXT
);

CREATE INDEX IF NOT EXISTS idx_xbrl_company_report ON xbrl_normalized(company_id, report_date);

CREATE TABLE IF NOT EXISTS fundamental_metrics (
  company_id TEXT,
  report_date DATE,
  total_assets REAL,
  cash_and_equivalents REAL,
  short_term_investments REAL,
  marketable_securities REAL,
  total_liabilities REAL,
  short_term_liabilities REAL,
  long_term_liabilities REAL,
  shareholders_equity REAL,
  revenue REAL,
  operating_income REAL,
  net_income REAL,
  eps REAL,
  PRIMARY KEY(company_id, report_date)
);

CREATE INDEX IF NOT EXISTS idx_fundamentals_company ON fundamental_metrics(company_id, report_date DESC);

CREATE TABLE IF NOT EXISTS analysis_meta (
  key TEXT PRIMARY KEY,
  value TEXT
);

-- 指標別テーブル
CREATE TABLE IF NOT EXISTS net_net_params (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  param_name TEXT,
  param_value REAL
);

CREATE TABLE IF NOT EXISTS oneil_metrics (
  company_id TEXT,
  report_date DATE,
  eps_growth_3y REAL,
  eps_growth_5y REAL,
  relative_strength REAL,
  PRIMARY KEY(company_id, report_date)
);

CREATE TABLE IF NOT EXISTS market_distribution_days (
  date DATE PRIMARY KEY,
  distribution_count INTEGER
);

CREATE TABLE IF NOT EXISTS detected_candidates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_id TEXT,
  detection_date DATE,
  detection_type TEXT,
  params JSON,
  score REAL,
  issue_created BOOLEAN DEFAULT 0
);
```

---

# 7. S3 保存戦略／ライフサイクル

## 7.1 バケット構造
```
s3://{bucket}/raw/xbrl/YYYY/ -- 生XBRL (individual files)
s3://{bucket}/raw/price/YYYYMMDD/ -- 生株価CSV
s3://{bucket}/db/latest.sqlite
s3://{bucket}/db/latest.sqlite.gz
s3://{bucket}/archive/xbrl/YYYY.tar.gz -- 年単位で圧縮
```

## 7.2 ライフサイクルルール
- `raw/xbrl/YYYY/` : PUT後30日→Standard-IA、90日→Glacier Deep Archive（またはすぐに年次で tar.gz化してDeep Archive移行）
- `db/` : 常に Standard, バージョニング有効
- 保持ポリシー: 生データは10年以上（EDINETの制限に依らず）保存

## 7.3 コスト最適化
- 年次アーカイブは tar.gz して Glacier Deep Archive に置く
- presigned URL の発行で直接ダウンロードを可能にし、公開は最小の有効期間（7日）に制限

---

# 8. ブラウザ内解析ロジックのフロー（1ファイルSPA）

## 8.1 技術スタック
- sqlite-wasm（ブラウザ内SQLite）
- vanilla JS / small framework optional
- lightweight-charts for plotting
- localForage (IndexedDB) for caching downloaded DB

## 8.2 起動フロー
1. ページ読み込み → query param から `db_url`（presigned URL）を取得
2. ローカルキャッシュに同一ハッシュのDBがあるか確認
3. キャッシュがなければ fetch(db_url) で gz版をダウンロードし、IndexedDBに保存
4. sqlite-wasm で DB をオープン
5. クライアントサイドで初期クエリ（会社一覧、ランキングトップ100）を実行
6. UI を描画（ランキング/チャート）

## 8.3 インタラクション
- パラメータ変更（割引率、期間など） → クエリを動的に組み立てて再計算
- 銘柄クリック → 詳細（財務/チャート）を表示（DBクエリ）
- CSVエクスポート機能（client-sideでSQL結果をCSV化）

## 8.4 パフォーマンス対策
- 必要な列のみSELECT
- LIMIT / OFFSET と仮想スクロールでデータ量制御
- Chartは軽量化（データダウンサンプリング）
- IndexedDBに圧縮DBを保存して再利用

---

# 9. 各ランキング算出ロジック（数式 & 疑似コード）

## 9.1 ネットネットバリュー（NNV）
### 定義（ブログ記載準拠）
- NetNetAssets = Σ(discounted_immediately_liquid_assets) - TotalLiabilities
- NetNetPBR = MarketCapitalization / NetNetAssets
- 解釈: NetNetPBR < 1 → 割安

### 変数定義
- Cash = cash_and_equivalents
- MarketableSecurities = marketable_securities
- ShortTermInvestments = short_term_investments
- Receivables = receivables * discount_receivables_rate
- Inventory = inventory * discount_inventory_rate
- TotalLiquidity = Cash + MarketableSecurities + ShortTermInvestments + DiscountedReceivables + DiscountedInventory
- NetNetAssets = TotalLiquidity - TotalLiabilities
- MarketCap = share_count * latest_close_price

### 数式
```
DiscountedReceivables = Receivables * r_receivables
DiscountedInventory = Inventory * r_inventory
TotalLiquidity = Cash + MarketableSecurities + ShortTermInvestments + DiscountedReceivables + DiscountedInventory
NetNetAssets = TotalLiquidity - TotalLiabilities
NetNetPBR = MarketCap / NetNetAssets
```

### 例: スコア
- Score_NNV = 1 / NetNetPBR  (大きいほど魅力)
- フィルター: NetNetAssets > 0, MarketCap > 0

### 疑似コード
```
for each company:
  load latest fundamentals
  compute TotalLiquidity
  NetNetAssets = TotalLiquidity - total_liabilities
  if NetNetAssets <= 0: skip
  MarketCap = shares_outstanding * price
  NetNetPBR = MarketCap / NetNetAssets
  score = 1.0 / NetNetPBR
  if NetNetPBR < threshold: add to ranking
```

## 9.2 オニール成長株スクリーニング
### 指標
- EPS Growth Rate (3yr, 5yr)
- Relative Strength (RS): 52週/13週の株価パフォーマンスを市場平均と比較
- 売上・利益の一致した成長パターン

### EPS増加率（年率）
```
EPS_growth_ny = ((EPS_t / EPS_{t-n})^(1/n) - 1) * 100  -- 年率換算
```

### Relative Strength（簡易）
```
RS = (Price_rise_company)/(Price_rise_market_index) * 100
Price_rise_company = (price_now - price_n_days_ago)/price_n_days_ago
```

### スコア合成
```
Score_oneil = w_eps * normalized(EPS_growth) + w_rs * normalized(RS) + w_rev * normalized(revenue_growth)
```
重みは調整可能（デフォルト: w_eps=0.5, w_rs=0.3, w_rev=0.2）

### シグナル点灯条件（例）
- EPS_growth_3y > 20% AND RS > 70 → シグナル

## 9.3 マーケット天井検出（分配日）
### ロジック
- Distribution day: 特定銘柄群の下落幅や売買代金の分配的な終値下落をカウントする
- カウントがある閾値を超えると注意シグナル

### 疑似コード
```
for each day in window:
  count = 0
  for each leading_stock:
    if price_drop_percentage > drop_threshold and volume > volume_threshold:
      count += 1
  distribution_days[day] = count
if rolling_sum(distribution_days, lookback) > distribution_threshold:
  market_alert = True
```

---

# 10. 通知（GitHub Issue）仕様

## 10.1 Issue 内容テンプレート
- Title: `[AutoDetect] {ticker} - {detection_type} - {YYYY-MM-DD}`
- Body:
  - summary: 指標 & スコア
  - key metrics: NetNetPBR, EPS Growth, RS, MarketCap
  - link: presigned URL to SQLite / analysis page with query param to open that ticker
  - attachments: JSON ペイロード

## 10.2 作成方法
- `POST /repos/{owner}/{repo}/issues` using GITHUB_TOKENのスコープ
- 既存 issue 検出ロジック: 同一 ticker & detection_type の未クローズ issue が無ければ作成

---

# 11. CI/CD とデプロイ手順

## 11.1 開発フロー
- feature branch → PR → code review → merge to main → GitHub Actions runs
- gh-pages ブランチへ HTML を push して GitHub Pages を更新

## 11.2 デプロイ手順（簡易）
1. mainにマージ
2. Actions が走り、latest.sqlite を S3 にアップロード
3. presigned URL を Actions summary に書き込み
4. gh-pages を更新して公開

## 11.3 GitHub Actions ワークフロー YAML（サンプルは付録参照）

---

# 12. セキュリティ／認証／権限設計

- S3: バケットポリシーは private; read は presigned url 経由
- GitHub Token: Actions レベル (レポジトリスコープの権限最小化)
- Secrets: AWSキーは GitHub Secrets に保存
- DBに機密情報は保存しない
- presigned URL 有効期限は 7 日（configurable）

---

# 13. テスト計画

## 13.1 単体テスト
- xbrl_parser: サンプルXBRL → 正しいタグマッピングを返す
- import_to_sqlite: CSV→DBに正しく upsert

## 13.2 統合テスト
- 小規模統合（3社分のXBRL + 株価）で GitHub Actions ワークフローをローカル実行（act 等）

## 13.3 回帰テスト
- 指標の既知入力→期待出力（数値ベース）
- CI にテスト用SQLiteを置き、アサーションを実行

---

# 14. 運用・監視・障害復旧

## 14.1 監視
- GitHub Actions: failed workflows email
- S3: 異常アクセスログ (optional)
- DB整合性: 毎週 integrity_check を実行

## 14.2 障害復旧
- DB破損時: S3バージョニングから前日の sqlite を復元
- XBRLロス: archive tar.gz から復元

---

# 15. 他AIが再現するための最短手順（リプロデュースガイド）

## 前提
- AWSアカウント、GitHubリポジトリ、GITHUB_TOKENの準備

## 手順
1. リポジトリを clone
2. GitHub Secrets に AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / S3_BUCKET / PRICE_API_KEY を設定
3. requirements.txt を使って仮想環境を作成
4. `python scripts/create_schema.py` を実行して local latest.sqlite を生成
5. `python scripts/fetch_xbrl.py --limit 50` を使って最初のXBRLを取得し raw/ に保存
6. `python scripts/parse_xbrl.py` を実行して normalized/ を出力
7. `python scripts/import_to_sqlite.py` を実行して sqlite を更新
8. `python scripts/analyze.py --db latest.sqlite` を実行して検出ロジックを実行
9. results.json を見て `python scripts/create_github_issue.py --payload results.json` をローカル実行
10. GitHub Pages 用の `index.html` を作成し presigned URL クエリで開く

---

# 16. 付録: サンプルコード / クエリ / YAML

※以下は再現用の抜粋サンプル（実行は自己責任）

## 16.1 サンプルSQLクエリ（ネットネット上位100）
```sql
WITH latest_fund AS (
  SELECT company_id, max(report_date) as rd
  FROM fundamental_metrics
  GROUP BY company_id
)
SELECT c.company_id, c.ticker, f.total_liabilities, f.cash_and_equivalents, f.marketable_securities,
  (f.cash_and_equivalents + f.marketable_securities) - f.total_liabilities AS net_net_assets,
  (select close from stock_prices_daily p where p.company_id=c.company_id order by date desc limit 1) as last_price,
  (select close from stock_prices_daily p where p.company_id=c.company_id order by date desc limit 1) * (select shares_outstanding from companies where company_id=c.company_id) as market_cap
FROM companies c
JOIN fundamental_metrics f ON c.company_id = f.company_id
WHERE f.report_date = (SELECT max(report_date) FROM fundamental_metrics WHERE company_id = c.company_id)
ORDER BY (market_cap / ((f.cash_and_equivalents + f.marketable_securities) - f.total_liabilities)) ASC
LIMIT 100;
```

## 16.2 GitHub Actions ワークフロー（抜粋）
```yaml
name: daily-update
on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch: {}

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install
        run: pip install -r requirements.txt
      - name: Download latest sqlite
        run: |
          aws s3 cp s3://${{ secrets.S3_BUCKET }}/db/latest.sqlite ./ || true
      - name: Fetch prices
        run: python scripts/fetch_prices.py --since-file latest.sqlite
      - name: Fetch XBRL
        run: python scripts/fetch_xbrl.py --since-file latest.sqlite
      - name: Parse XBRL
        run: python scripts/parse_xbrl.py --input raw/xbrl --out normalized
      - name: Import
        run: python scripts/import_to_sqlite.py --db latest.sqlite --input normalized
      - name: Analyze
        run: python scripts/analyze.py --db latest.sqlite --out results.json
      - name: Create Issues
        run: python scripts/create_github_issue.py --payload results.json
      - name: Upload DB
        run: |
          aws s3 cp latest.sqlite s3://${{ secrets.S3_BUCKET }}/db/latest.sqlite
```

## 16.3 サンプル Python モジュール構成
```
./scripts/
  fetch_xbrl.py
  parse_xbrl.py
  fetch_prices.py
  import_to_sqlite.py
  analyze.py
  create_github_issue.py
  create_schema.py

./lib/
  xbrl_parser/
  sqlite_utils/
  analyzers/
```

---

# 最後に（エンジニア向け注記）
この仕様書は「他AIが再現可能」なレベルを目指しており、現段階で実装に必要なほとんどの設計情報を含んでいます。次の推奨タスク:
- `scripts/create_schema.py` を実装してDDLを自動生成
- XBRLタグのマッピング表（EDINETタグ→内部フィールド）を作成
- パラメータのデフォルト値（割引率・閾値等）を config.yaml にて管理

必要なら、これをさらに分割して `docs/` 配下の複数Markdownファイル、Spec Kit テンプレート（/speckit.specify 用プロンプト）に変換します。

