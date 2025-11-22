
## 概要
本仕様書は、東京電力、中部電力、およびJERAの経営状況を可視化・分析するためのAI搭載ダッシュボードアプリケーションの開発仕様を定義する。本システムの最大の特徴は、インフラとしてGitHubリポジトリのみを利用し、サーバーレスかつ低コストでの運用を実現する点にある。GitHub Actionsによる日次バッチ処理で各社の財務諸表、決算報告、株価などの公開情報を自動収集し、単一のSQLiteデータベースファイルに集約する。生成されたデータベースはGitHub Pagesでホストされる静的ウェブページから動的に読み込まれ、ブラウザ上で高度なデータ解析とインタラクティブなグラフ表示を可能にする。これにより、利用者は常に最新の経営指標や業績推移をダッシュボード形式で確認できる。

## 詳細レポート

### 1. プロジェクト概要

**目的とスコープ**
本プロジェクトの目的は、東京電力ホールディングス（証券コード: 9501）、中部電力（証券コード: 9502）、および両社の合弁会社であるJERAの経営状況を定量的かつ多角的に分析するためのダッシュボードアプリケーションを構築することである。利用者は、主要な財務指標、業績推移、株価動向などを直感的に把握し、3社の比較分析を行うことができる。

**対象企業**
*   東京電力ホールディングス株式会社
*   中部電力株式会社
*   株式会社JERA

**コアコンセプト**
*   **サーバーレスアーキテクチャ:** 専用サーバーやデータベースインフラを必要とせず、GitHubエコシステム内で完結させることで、運用コストと管理負荷を極小化する[[194](https://crexgroup.com/ja/development/tools/github-actions-tutorial/)]。
*   **データ集約とポータビリティ:** 全てのデータを単一のSQLiteファイルに集約する。このファイルは移植性が高く、ローカル環境での詳細分析や、他のツールとの連携も容易である[[4](https://qiita.com/shikuno_dev/items/13de104aa2c2adf8aead)][[9](https://www.javadrive.jp/sqlite/)]。
*   **自動化されたデータパイプライン:** GitHub Actionsを用いて、データの収集、加工、データベース更新、通知までの一連のプロセスを完全に自動化する[[31](https://qiita.com/ishigami_masato/items/f38b8d27962ff2248598)][[183](https://qiita.com/ishigami_masato/items/f38b8d27962ff2248598)]。
*   **リッチなクライアントサイド分析:** ブラウザのJavaScriptとWebAssembly（WASM）を用いてSQLiteファイルを直接操作し、サーバーへのリクエストなしに動的なデータ可視化とインタラクティブな分析を実現する。

### 2. システムアーキテクチャ

**全体構成図**
本システムのアーキテクチャは、データ収集層、データ処理・格納層、そしてデータ提供・可視化層の3層で構成される。全ての処理はGitHubリポジトリを中心に連携する。

![GitHub Actionsを中心としたシステムアーキテクチャの概念図](https://firebasestorage.googleapis.com/v0/b/videotoblog-35c6e.appspot.com/o/%2Fusers%2FFCPc7wfTcUgdi6tJMUoPkQT6kG93%2Fblogs%2F1TAb140BOAwkGNRXddN1%2Fscreenshots%2Fae9aa315-8851-4af8-9c66-e59c7c187091.webp?alt=media&token=23f76ef6-185a-45e8-a86b-608568242ac1)
*(画像はGitHub Actionsの概念を示すもので、本プロジェクトのアーキテクチャを模式的に表現)*

**フロー概要:**
1.  **データ収集 (GitHub Actions):** スケジュールされた日次バッチが、EDINET、TDnet、各社IRサイト、株価情報サイトなどから最新の財務・株価データをダウンロードする[[2](https://qiita.com/koduki/items/e90ee1fea5aa75071d95)][[154](https://qiita.com/koduki/items/e90ee1fea5aa75071d95)]。
2.  **データ処理と格納 (GitHub Actions & SQLite):** 収集した生データをパース・正規化し、リポジトリ内のSQLiteデータベースファイル (`financial_data.sqlite`) に追記・更新する[[176](https://devops-blog.virtualtech.jp/entry/20250514/1747187780)]。更新されたデータベースファイルはリポジトリにコミットされる。
3.  **データ提供 (GitHub Pages):** GitHub Pagesでホストされた分析ダッシュボード（静的HTML/JS/CSS）が、リポジトリ内の最新のSQLiteファイルへのリンクを持つ。
4.  **可視化 (ブラウザ):** ユーザーがダッシュボードにアクセスすると、ブラウザがJavaScriptを用いてSQLiteファイルをダウンロードし、`sql.js`ライブラリを介してデータベースをメモリ上に展開。動的にクエリを実行し、`Chart.js`などのライブラリで結果をグラフ描画する。
5.  **通知 (GitHub Issues):** 日次バッチはデータ解析も行い、株価の異常変動や重要な財務指標の変化を検知した場合、GitHub Issueを自動で作成し、関係者に通知する[[201](https://qiita.com/shinya_ichinoseki/items/4e2bd4ad27c035e34698)]。

### 3. データモデルと管理

**収集対象データ**
以下の情報を定期的に収集し、データベースに格納する。

| データカテゴリ | 具体的な内容 | 主なデータソース |
| :--- | :--- | :--- |
| **財務諸表** | 貸借対照表(B/S)、損益計算書(P/L)、キャッシュフロー計算書(C/F)の各項目[[55](https://www.tepco.co.jp/corporateinfo/illustrated/accounting/balance-sheet-consolidated-j.html)][[61](https://www.tepco.co.jp/corporateinfo/illustrated/accounting/statement-income-consolidated-j.html)][[90](https://www.ullet.com/%E6%9D%B1%E4%BA%AC%E9%9B%BB%E5%8A%9B%E3%83%9B%E3%83%BC%E3%83%AB%E3%83%87%E3%82%A3%E3%83%B3%E3%82%B0%E3%82%B9/%E6%B1%BA%E7%AE%97%E6%9B%B8)] | EDINET API, 各社IRサイトの決算短信PDF[[48](https://www.tepco.co.jp/about/ir/library/results/)][[66](https://www.tepco.co.jp/about/ir/library/results/bk.html)][[93](https://www.tepco.co.jp/about/ir/library/results/)] |
| **決算関連資料** | 決算説明会資料、ファクトブック、有価証券報告書[[49](https://www.tepco.co.jp/about/ir/library/securities_report/)] [[54](https://www.tepco.co.jp/about/ir/library/presentation/)] [[75](https://www.chuden.co.jp/ir/ir_siryo/yukashoken/)]| 各社IRサイト[[94](https://www.jera.co.jp/ir/library/fr)][[95](https://www.chuden.co.jp/ir/ir_zaimu/)] |
| **株価データ** | 日足・週足の始値, 高値, 安値, 終値, 出来高[[98](https://finance.yahoo.co.jp/quote/9502.T)] [[100](https://finance.yahoo.co.jp/quote/9501.T)] [[148](https://finance.yahoo.co.jp/quote/9502.T)]| 株価情報提供API (Yahoo Finance等) |
| **経営指標** | ROE, ROA, 自己資本比率, D/Eレシオ, PER, PBR, 配当利回りなど[[99](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/)] [[102](https://www.tepco.co.jp/about/ir/library/factbook/)] [[142](https://www.nikkei.com/nkd/company/kessan/?scode=9501)]| 収集した財務・株価データから算出 |

**SQLiteデータベース設計**
データベースは単一のファイル (`financial_data.sqlite`) として管理される。以下に主要なテーブルのスキーマ定義例を示す。

*   **`companies` (企業マスタ)**
    *   `company_id` (INTEGER, PK): 企業ID
    *   `company_name` (TEXT): 企業名 (例: 東京電力ホールディングス)
    *   `ticker_symbol` (TEXT): 証券コード (例: 9501)

*   **`financial_statements` (財務データ)**
    *   `statement_id` (INTEGER, PK): データID
    *   `company_id` (INTEGER, FK): 企業ID
    *   `fiscal_year` (INTEGER): 会計年度
    *   `quarter` (INTEGER): 四半期 (1Q, 2Q, 3Q, 4Q)
    *   `metric_name` (TEXT): 指標名 (例: 売上高, 営業利益)
    *   `metric_value` (REAL): 指標値
    *   `announced_date` (TEXT): 発表日

*   **`stock_prices` (株価データ)**
    *   `price_id` (INTEGER, PK): データID
    *   `company_id` (INTEGER, FK): 企業ID
    *   `date` (TEXT): 日付
    *   `open` (REAL): 始値
    *   `high` (REAL): 高値
    *   `low` (REAL): 安値
    *   `close` (REAL): 終値
    *   `volume` (INTEGER): 出来高

![DB Browser for SQLiteでのデータベース管理イメージ[14]](https://www.1-firststep.com/wp-content/uploads/2019/03/sqlite-3-650x410.jpg)
*DB Browser for SQLiteなどのツールで、ローカルでのデータ確認や編集が容易に行える[[166](https://www.1-firststep.com/archives/7445)][[195](https://sqlite.cheap.jp/db-browser-for-sqlite/)]。*

### 4. 自動化ワークフロー (GitHub Actions)

リポジトリの `.github/workflows/` ディレクトリに、日次更新用のワークフローファイル (`daily-update.yml`) を配置する[[32](https://learn.microsoft.com/ja-jp/azure/azure-sql/database/connect-github-actions-sql-db?view=azuresql)][[45](https://learn.microsoft.com/ja-jp/azure/mysql/flexible-server/quickstart-mysql-github-actions)][[184](https://learn.microsoft.com/ja-jp/azure/azure-sql/database/connect-github-actions-sql-db?view=azuresql)]。

**ワークフローのトリガー設定**
ワークフローは、毎日日本時間午前6時（UTC 21時）に定期実行される。また、テストや手動更新のために `workflow_dispatch` トリガーも設定する[[12](https://zenn.dev/tacoms/articles/d54e7b70481efc)][[159](https://qiita.com/masa_code/items/b8757eb53590afe9acfa)]。

```yaml
name: Daily Financial Data Update

on:
  schedule:
    # JST 06:00 (UTC 21:00) に毎日実行
    - cron: "0 21 * * *"
  workflow_dispatch: # 手動実行を許可
```

**日次バッチ処理の詳細**
ワークフローは以下のステップで構成される。

1.  **環境設定:**
    *   リポジトリをチェックアウトする。
    *   PythonやNode.jsなど、データ収集・加工スクリプトの実行環境をセットアップする。

2.  **データ取得:**
    *   Pythonスクリプト（例: `scraper.py`）を実行し、各データソースから最新の財務データや株価データをダウンロードする。
    *   データ欠損を防ぐため、スクリプトはSQLite内の最新データ日付を取得し、それ以降の差分データのみを対象とする。

3.  **データベース更新:**
    *   ダウンロードした生データ（JSON, CSV, PDFなど）をパースし、正規化する。
    *   SQLiteデータベースに接続し、新しいデータを `INSERT` または `UPDATE` する[[176](https://devops-blog.virtualtech.jp/entry/20250514/1747187780)]。この処理はアトミックに行い、途中で失敗した場合はロールバックする設計が望ましい。

4.  **リポジトリへのコミット:**
    *   更新された `financial_data.sqlite` ファイルと、ダウンロードした生データをリポジトリにコミット＆プッシュする。これにより、処理の再現性とデータの透明性が確保される。

5.  **解析と通知:**
    *   データベース内のデータを分析し、特定の条件（例: ROEが前四半期比で10%以上変動、株価が20日移動平均線をゴールデンクロス）を検出する。
    *   条件に合致した場合、GitHub CLI (`gh`) を使用してリポジトリにIssueを自動作成する。Issueのタイトルや本文には、検知した事象の詳細を記載する。

**ワークフローのYAMLサンプル**
```yaml
jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Download latest data
        run: python scripts/download_data.py

      - name: Update SQLite database
        run: python scripts/update_database.py

      - name: Commit and push if changes
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add .
          if ! git diff --staged --quiet; then
            git commit -m "Update financial data for $(date -u +'%Y-%m-%d')"
            git push
          fi

      - name: Analyze data and create issue if needed
        if: success()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/analyze_and_notify.py | gh issue create --title "Daily Financial Alert" --body -
```

*GitHub ActionsのUI上で、毎日のバッチ処理の実行状況を確認できる[[18](https://kimoba.com/kasegu/github-actions-workflow.html)][[23](https://ai-kidou.jp/github-actions-jisou-ai-workflow/)]。*

### 5. 分析ダッシュボード (フロントエンド)

**技術スタック**
*   **ホスティング:** GitHub Pages
*   **言語:** HTML, CSS, JavaScript (ES6+)
*   **データベース操作:** [sql.js](https://sql.js.org/) (SQLiteのWebAssemblyポート)
*   **データ可視化:** [Chart.js](https://www.chartjs.org/) または [D3.js](https://d3js.org/)
*   **UIフレームワーク (任意):** React, Vue.js, or Svelte (静的サイトとしてビルド)

**主要機能**
1.  **動的データロード:** ページアクセス時、JavaScriptがURLのクエリパラメータからSQLiteファイルのパスを取得し、`fetch` APIを用いて非同期にダウンロードする。
2.  **ブラウザ内解析:** ダウンロードしたSQLiteファイル（バイナリデータ）を `sql.js` に渡し、ブラウザのメモリ上でデータベースを開く。SQLクエリを発行して必要なデータを抽出し、JSON形式に変換する。
3.  **インタラクティブな可視化:** 抽出したデータを `Chart.js` に渡し、各種グラフ（時系列、棒、レーダーチャートなど）を描画する。ユーザー操作（期間変更、指標選択など）に応じて、サーバー通信なしで即座にグラフを再描画する。
4.  **ローカルファイル対応:** ユーザーがローカルに持つSQLiteファイルをドラッグ＆ドロップまたはファイル選択で読み込み、同様の分析を行える機能を提供する。これにより、開発やカスタマイズが容易になる。

**UI/UX設計案**
*   **レイアウト:** 各企業（東京電力, 中部電力, JERA）をカード形式で並べ、主要なサマリー指標を表示。
*   **詳細ビュー:** カードをクリックすると、詳細な分析ページに遷移。収益性、健全性、株価などのタブで情報を整理。
*   **比較機能:** 複数の企業の同一指標を一つのグラフに重ねて表示する機能。

![中部電力の業績ハイライトグラフの例[149]](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/img/img_01.webp)
*ダッシュボードでは、このような売上高や営業利益の推移グラフをインタラクティブに表示する[[149](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/)]。*

### 6. 分析指標とインサイトの提案

ダッシュボードでは、以下の指標を中心に分析と可視化を行うことを提案する。

**収益性分析**
*   **ROE (自己資本利益率) / ROA (総資産利益率):** 資本効率性を示す最重要指標。3社の推移を比較し、事業の収益力を評価する[[99](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/)] [[117](https://irbank.net/E04502/results)] [[126](https://minkabu.jp/stock/9501/settlement)]。
*   **売上高営業利益率:** 本業での稼ぐ力を示す。燃料費調整制度の影響も考慮に入れて分析する。
*   **JERAの期ずれ影響:** JERAの決算では、燃料価格の変動が料金に反映されるまでのタイムラグ（期ずれ）が利益を大きく左右する[[64](https://www.texreport.co.jp/articles/91672)][[82](https://www.jera.co.jp/ir/highlight)]。期ずれ影響額とそれを除いた実質利益を併記し、事業の実態を正確に把握する。

**財務健全性分析**
*   **自己資本比率:** 企業の財務安定性を示す。電力業界は巨大な設備投資が必要なため、この指標の安定性が重要となる[[108](https://www.tepco.co.jp/corporateinfo/illustrated/accounting/)][[129](https://www.rakuten-sec.co.jp/web/special/chuden/pdf/pdf-01.pdf?20250919)][[142](https://www.nikkei.com/nkd/company/kessan/?scode=9501)]。
*   **D/Eレシオ (デット・エクイティ・レシオ):** 有利子負債が自己資本の何倍かを示す。負債への依存度を評価する[[86](https://strainer.jp/companies/JP-9502/financials/NetDebt?period=quarterly)][[149](https://www.chuden.co.jp/ir/ir_zaimu/gyoseki/)]。
*   **有利子負債残高:** 負債の絶対額の推移を監視する[[73](https://www.tepco.co.jp/corporateinfo/illustrated/accounting/)][[86](https://strainer.jp/companies/JP-9502/financials/NetDebt?period=quarterly)]。

**株価関連指標 (東京電力・中部電力)**
*   **PER (株価収益率) / PBR (株価純資産倍率):** 株価の割安・割高感を評価する。業界平均や過去の推移と比較する[[140](https://finance.yahoo.co.jp/quote/9501.T/forum)][[148](https://finance.yahoo.co.jp/quote/9502.T)][[150](https://finance.yahoo.co.jp/quote/9501.T)]。
*   **配当利回り:** 株主還元の姿勢を評価する。

**企業間連携の分析**
*   **JERAの業績が親会社に与える影響:** JERAは東京電力と中部電力が50%ずつ出資する持分法適用会社である。JERAの純利益は、両社の連結決算において「持分法による投資利益」として計上される[[58](https://www.nikkei.com/article/DGXZQOUC313AU0R31C25A0000000/)]。この影響額を可視化し、親会社の業績への貢献度を分析する。

### 7. 運用設計

**エラーハンドリングと通知**
*   GitHub Actionsのワークフローが失敗した場合、リポジトリの所有者にはデフォルトでメール通知が届く[[5](https://qiita.com/shinya_ichinoseki/items/4e2bd4ad27c035e34698)]。より高度な通知として、Slack連携などを追加することも可能である[[201](https://qiita.com/shinya_ichinoseki/items/4e2bd4ad27c035e34698)]。
*   データ取得スクリプトにはリトライロジックを組み込み、一時的なネットワークエラーに対応する。

**データ整合性の担保**
*   データベースの更新は、最新データの取得とパースが全て成功した後にのみ行う。
*   SQLiteのトランザクション機能を利用し、一連の書き込み処理が完全に成功するか、完全に失敗（ロールバック）するかのどちらかになるように保証する。

**メンテナンス計画**
*   データソース（各社IRサイトなど）のHTML構造やAPI仕様の変更は、データ取得失敗の主要因となる。定期的に（例: 四半期ごと）スクレイピングロジックの動作確認と必要に応じた修正を行う。

---
