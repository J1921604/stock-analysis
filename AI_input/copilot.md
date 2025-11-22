
### プロジェクト仕様書: 東京電力 / 中部電力 / JERA ダッシュボードアプリ（仕様書.md）

概要

- 目的: 東京電力（TEPCO）、中部電力（Chubu）、JERA の財務諸表・決算・関連データを日次で収集し、SQLite 単一ファイルで一元管理。ブラウザ／ローカルで同一の SQLite を読み込み、企業別カードに「現在値・推移グラフ・解説」を表示する軽量ダッシュボードを提供する。
- 運用方針: 必要なインフラは GitHub リポジトリのみ。日次 GitHub Actions バッチでデータ取得→正規化→SQLite 追記→アップロード→解析→通知の一連を完結する。IR/決算資料は各社が公開する資料を一次ソースとする [株式会社JERA](https://www.jera.co.jp/static/files/corporate/ir/pdf/securities_report2106.pdf) [中部電力](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/) [東京電力グループ](https://www4.tepco.co.jp/about/ir/library/presentation/pdf/231031setsu-j.pdf)。

---

### 全体アーキテクチャ

- ストレージ: 単一 SQLite ファイル（./data/speckit_finance.sqlite）
- 管理リポジトリ: GitHub リポジトリ（コード・ワークフロー・最新 SQLite を格納）
- 自動化: GitHub Actions（cron による日次バッチ、手動トリガー可）
    - Cron 例: 実行は毎日 JST 18:00（例 - cron: "0 9 * * *"）でスケジュール、workflow_dispatch を併用（手動テスト用）。
- 配信: GitHub Pages（静的 HTML + JS）で解析 UI をホスト。ページは毎日生成される presigned URL（もしくはリポジトリ内最新ファイル）をクエリに含め、ブラウザは JS で SQLite をダウンロードしてキャッシュ、完全クライアント側で解析・可視化。
- 通知: GitHub Issues を利用して日次解析結果や異常を登録。Actions が Issue を作成し、リポジトリオーナーに通知メールが送られる。

---

### データフロー（日次バッチの順序）

1. SQLite をダウンロード（最新ファイル取得）。
2. 当日更新の原データ（株価 CSV、EDINET/各社IR PDF/XLSX、為替、燃料価格等）をダウンロード。
3. 生データをパース → 正規化（スキーマに沿って）→ SQLite に「差分追加（SQLite 内の最新日付以降のみ取得）」。
4. 生データファイルを sync（./raw/ YYYY-MM-DD/ に保存）。
5. 解析・集約処理（指標の算出、アラート判定）。
6. 最後に最新の SQLite を上書き保存してリポジトリにコミット＆プッシュ（アップロードは最終ステップで実施）。
7. 解析結果要約を GitHub Pages 用に更新し、presigned URL をクエリに含む静的ページリンクを作成。
8. 必要な通知（Issue 作成や重大アラート）を生成。

運用上のポイント

- CI 失敗で欠損を防ぐため、取得は SQLite 内の最新日付以降のみを対象にする（冪等性確保）。
- 大きな生データ取得やパースはタイムアウト対策で段階化（小さなチャンク処理）する。
- SQLite ファイルは必ずワークフローの最後に書き換える。

---

### データモデル（主要テーブル案）

- companies (company_id, ticker, name_jp, name_en, icb_sector, created_at)
- raw_files (id, company_id, source_url, local_path, file_date, file_type, checksum, ingested_at)
- price_daily (id, company_id, date, close, open, high, low, volume, source)
- financial_statements (id, company_id, report_date, period_type, statement_type, metric_key, metric_value, currency, unit)
- ratios_daily (id, company_id, date, pe, roe, roa, ev_ebitda, debt_equity, current_ratio)
- fuel_prices (id, date, fuel_type, price_usd_per_unit, source)
- exchange_rates (id, date, pair, rate)
- alerts (id, created_at, severity, title, body, linked_entities)
- metadata (key, value)

設計原則

- 単一行アイテムは日付＋キーで一意化。時間序列は date 型で管理。
- 金額は常に最小単位（例: 百万円 → value と unit 列）で保存して正規化。
- 生データは raw_files に残して再現可能性を担保。

---

### 収集すべき情報と推奨指標（提案）

- 以下テーブルは「指標;目的;一次ソース;更新頻度;可視化形式」の形式で示す。

|指標|目的|一次ソース|更新頻度|可視化|
|---|---|---|---|---|
|売上高;企業規模とトレンド;各社決算資料（有価証券報告書/決算説明資料）;四半期/年次;折れ線＋前年同期比|
|営業利益;コア業績;同上;四半期/年次;折れ線＋率（%）|
|経常利益 / 純利益;全体収益性;同上;四半期/年次;棒＋テーブル|
|営業CF / 投資CF / 財務CF;キャッシュフロー健全性;同上;四半期/年次;積み上げ棒|
|有利子負債残高 (D);財務レバレッジ;決算注記;四半期/年次;ライン＋D/E 比|
|D/E レシオ;財務健全性;決算書;四半期/年次;折れ線|
|ROE / ROA;収益性指標;決算書;四半期/年次;比較レーダー or ランク表示|
|EPS / 希薄化後EPS;株主還元状況;決算書;四半期/年次;折れ線|
|配当利回り;投資家向け価値;株価データ＋決算;日次更新（株価）;ライン＋注記|
|発電量構成（燃料別）;事業ミックス/脱炭素指標;各社IR/説明資料;年次/四半期;積み上げ面グラフ|
|燃料費調整や燃料費影響額;収益変動要因;決算資料/注記;四半期/年次;注釈付き時系列|
|燃料価格（LNG/石炭/原油）;コストドライバー;市場データ;日次;ライン|
|為替（USD/JPY）;燃料コスト影響;市場データ;日次;ライン|
|債務償還スケジュール;流動性リスク;注記/補助資料;年次;表|
|発電所別稼働率 / 送配電投資;オペレーショナル指標;IR/事業報告;四半期/年次;地図＋棒|
|ESG 指標（Scope1/2 排出量、再エネ比率等）;移行リスク;IR/サステナ報告;年次;トレンドライン|
|JERA の事業別収益（発電/燃料トレード等）;グループ・戦略的影響;JERA 決算資料;四半期/年次;カード内解説 [株式会社JERA](https://www.jera.co.jp/static/files/corporate/ir/pdf/securities_report2106.pdf)|
|連結 vs 単体比較;グループ構造の透明化;各社有価証券報告書;四半期/年次;比較差分表示 [中部電力](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/) [東京電力グループ](https://www4.tepco.co.jp/about/ir/library/presentation/pdf/231031setsu-j.pdf)|

（注）各社は決算資料や投資家向けデータブックを公開しているため、財務諸表や発電構成・ESG は一次ソースから取得可能である [株式会社JERA](https://www.jera.co.jp/static/files/corporate/ir/pdf/securities_report2106.pdf) [中部電力](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/) [東京電力グループ](https://www4.tepco.co.jp/about/ir/library/presentation/pdf/231031setsu-j.pdf)。

---

### UI 要件（カード設計）

- 企業カード（TEPCO / 中部 / JERA）
    - ヘッダー: 会社名、ティッカー、最終更新日、主要サマリ（EPS、配当、時価総額）
    - メトリック行: 要点（売上・営業利益・純利益・ROE・D/E）を数値＋前期差分で表示
    - グラフセクション:
        - 株価（ローソク or 終値）: 日次〜年次の切替
        - 主要業績トレンド（売上・営業利益）: 四半期/年度トグル
        - キャッシュフローと負債: 積み上げ棒＋D/E ライン
        - ESG / 発電構成: 積み上げ面グラフ
    - 解説パネル（自動生成/テンプレ化）:
        - 主要変動要因の自然言語要約（例: 燃料費上昇が営業利益を圧迫）と該当データのハイライト
        - リスク/注目点の短文（例: 「JERA の燃料トレード収益動向に注意」） [株式会社JERA](https://www.jera.co.jp/static/files/corporate/ir/pdf/securities_report2106.pdf)。
    - フィルタ／パラメータ: 比較企業選択、期間指定、インフレ/為替補正トグル
    - ダウンロード: ブラウザで利用中の SQLite を使って CSV をエクスポート（UI のボタンでローカル処理）

---

### データ取得・正規化の実装方針

- 取得順序: まず SQLite の最新日付を確認 → その日以降の更新分のみダウンロード（冪等処理）。
- IR PDF/XLSX: PDF はテキスト抽出（tabula/pyPDF）、XLSX は直接パース。EDINET（上場情報）は API または EDINET ファイルを利用。
- 株価: 信頼できる CSV API（Yahoo Finance 互換等）を日次で取得。
- 市場データ（燃料価格・為替）: 公的ソースまたは商用 API（無料枠で足りない場合は CSV 同期）を利用。
- 正規化ルール:
    - 金額は通貨と単位を分離して保存（例: 1,234 百万円 -> value=1234, unit=百万円, currency=JPY）。
    - 日付は ISO 形式（YYYY-MM-DD）で保存。
    - 同一指標のキー命名規則を厳格化（例: income_operating, profit_net, total_assets）。
- データ品質:
    - チェックリスト: 重複行、欠損、非数値を検出してログ化。重大エラーは Issue 作成（自動化）。

---

### GitHub Actions ワークフロー（主要ステップ／サンプル）

- トリガー: schedule (cron: "0 9 * * *") + workflow_dispatch
- ジョブ例:
    1. setup-environment（Python / Node / sqlite3）
    2. download-latest-sqlite（checkout; download latest speckit_finance.sqlite）
    3. fetch-raw-data（株価・IR・燃料・為替のダウンロード）
    4. parse-and-normalize（パース、正規化、差分抽出）
    5. ingest-to-sqlite（SQLite に追記）
    6. run-analytics（指標計算、アラート判定）
    7. commit-and-upload-sqlite（最終的に SQLite を上書きして push）
    8. update-pages-and-links（presigned URL を生成して Pages 用ファイル更新）
    9. notify-via-issue（Issue を作成。緊急は high severity）
- 実装注意:
    - SQLite 操作は排他ロックに注意して一貫性を保証する。
    - 長時間処理は分割して中間成果を raw_files に保存。

---

### セキュリティと運用、ガバナンス

- 機密情報: API キーやトークンは GitHub Secrets に格納（リポジトリコードに直書きしない）。
- バージョン管理: SQLite は大きくなるため LFS を検討。ただし「GitHub をストレージにする」設計であればサイズ管理ルールを設定。
- ロールバック: commit する直前の SQLite をバックアップ（例: ./backups/2025-11-22.sqlite）。
- 監査ログ: raw_files と metadata に取得ログを残す。
- データ保証: 重要な財務指標は「一次ソースの該当ページ URL とファイルチェックサム」を保存してトレーサビリティを担保。

---

### 自動解説（NLG）・アラート方針

- 自動要約テンプレート:
    - 例: 「{company} の {period} は {metric} が {value}（前期比 {delta}%）で、主因は {drivers}。」
- 重要アラート条件（サンプル）
    - 営業利益が前年比 -30% 以上下落 → severity: high
    - D/E が閾値（例 2.0）を超過 → severity: medium
    - 配当性向急変または無配発表 → severity: medium
    - データ欠損（期待する四半期データが未取得）→ severity: low→ Issue 作成
- Issue 内容: 自動生成本文に取得ログと該当 raw_file を参照するリンクを載せる。

---

### 実装スニペット（参考、擬似）

- Cron はプロジェクトで提示の通り設定:
    - on: schedule:
        - cron: "0 9 * * *" workflow_dispatch: true
- SQLite 差分取得ロジック（擬似）
    - latest_date = SELECT MAX(date) FROM price_daily WHERE company_id=?
    - fetch data WHERE date > latest_date

---

### 次のアクション（提案）

1. この仕様書をリポジトリ直下に「仕様書.md」として登録する（内容の最終確認は不要ならそのままコミット）。
2. GitHub Actions のワークフローテンプレート（jobs の雛形）を1つ作成してプルリクを作成。
3. 最初のデータパイプラインは TEPCO の最新決算 PDF と日次株価を対象に PoC を回し、正規化ルールを固める（TEPCO / 中部 / JERA は IR で主要資料を公開している点を利用） [東京電力グループ](https://www4.tepco.co.jp/about/ir/library/presentation/pdf/231031setsu-j.pdf) [中部電力](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/) [株式会社JERA](https://www.jera.co.jp/static/files/corporate/ir/pdf/securities_report2106.pdf)。
4. UI の最小実装は「会社カード × 1（株価 + 売上推移）」で始め、指標を順次追加。

---

参考（一次情報の所在）

- JERA 有価証券報告書等（決算・財務諸表） [株式会社JERA](https://www.jera.co.jp/static/files/corporate/ir/pdf/securities_report2106.pdf)。
- 中部電力 IR（業績・指標ハイライト） [中部電力](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/)。
- 東京電力 決算説明資料（プレゼン・注記） [東京電力グループ](https://www4.tepco.co.jp/about/ir/library/presentation/pdf/231031setsu-j.pdf)。
