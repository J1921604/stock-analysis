
# 東京電力・中部電力・JERA 経営状況ダッシュボード 仕様書

## 1. プロジェクト概要

### 1.1 目的

東京電力、中部電力、JERAの3社の財務状況と経営指標をリアルタイムで監視・分析するダッシュボードシステム

### 1.2 システム特徴

- インフラコスト: ゼロ (GitHubのみ使用)
- データベース: SQLite (単一ファイル管理)
- 自動更新: GitHub Actions による日次バッチ
- 分析環境: ブラウザ上で完結 (GitHub Pages)
- 通知機能: GitHub Issues 経由でメール通知

---

## 2. システムアーキテクチャ

### 2.1 全体構成図

```
┌─────────────────────────────────────────────────────┐
│ GitHub Repository                                   │
│                                                     │
│  ┌─────────────────┐  ┌──────────────────────┐   │
│  │ GitHub Actions  │  │ GitHub Pages         │   │
│  │ (Daily Batch)   │  │ (Static HTML/JS)     │   │
│  └────────┬────────┘  └──────────┬───────────┘   │
│           │                       │                │
│           ▼                       ▼                │
│  ┌─────────────────┐  ┌──────────────────────┐   │
│  │ data/           │  │ docs/                │   │
│  │ - power.db      │  │ - index.html         │   │
│  │ - raw/          │  │ - dashboard.js       │   │
│  └─────────────────┘  └──────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │ .github/workflows/daily-update.yml          │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
           │                           │
           ▼                           ▼
    ┌──────────────┐          ┌──────────────┐
    │ External APIs│          │ User Browser │
    │ - EDINET     │          │ - Analysis   │
    │ - 株価API     │          │ - Viz        │
    └──────────────┘          └──────────────┘
```

### 2.2 データフロー

```
1. データ収集 (GitHub Actions)
   └→ EDINET API / 株価API / IR情報
      └→ 生データ保存 (data/raw/)
         └→ パース & 正規化
            └→ SQLite更新 (data/power.db)
               └→ 分析処理
                  └→ GitHub Issues 作成 (通知)
                  └→ GitHub Pages 更新

2. データ閲覧 (Browser)
   └→ GitHub Pages アクセス
      └→ SQLite自動ダウンロード
         └→ ブラウザ内SQL実行
            └→ 動的ダッシュボード表示
```

---

## 3. データ収集仕様

### 3.1 対象企業

|企業名|証券コード|EDINET コード|特記事項|
|---|---|---|---|
|東京電力ホールディングス|9501|E04498|持株会社|
|中部電力|9502|E04285|-|
|JERA|非上場|E36542|東電・中部電の合弁|

### 3.2 収集データソース

#### 3.2.1 財務諸表 (EDINET API)

- **取得先**: 金融庁 EDINET API v2
- **更新頻度**: 四半期ごと (決算後2日以内)
- **取得内容**:
    - 有価証券報告書 (年次)
    - 四半期報告書
    - 訂正報告書

#### 3.2.2 株価情報

- **取得先**:
    - Yahoo Finance API (無料)
    - または Alpha Vantage API
- **更新頻度**: 日次
- **取得項目**:
    - 始値・高値・安値・終値
    - 出来高
    - 調整後終値

#### 3.2.3 IR情報

- **取得先**: 各社IR公式サイト
- **更新頻度**: 週次 (月曜チェック)
- **取得内容**:
    - プレスリリース
    - 決算説明資料
    - 中期経営計画

#### 3.2.4 業界指標

- **取得先**:
    - 資源エネルギー庁 統計情報
    - JEPX (日本卸電力取引所) API
- **更新頻度**: 日次/月次
- **取得項目**:
    - 電力需要量
    - スポット市場価格
    - 燃料価格 (LNG, 石炭, 原油)

---

## 4. データベース設計

### 4.1 テーブル構造

sql

```sql
-- 企業マスタ
CREATE TABLE companies (
    company_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    securities_code TEXT,
    edinet_code TEXT,
    industry TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 財務諸表 (BS)
CREATE TABLE balance_sheets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    quarter INTEGER, -- NULL = 年次
    report_date TEXT NOT NULL,
    
    -- 資産の部
    total_assets REAL,
    current_assets REAL,
    fixed_assets REAL,
    cash_and_deposits REAL,
    
    -- 負債の部
    total_liabilities REAL,
    current_liabilities REAL,
    long_term_debt REAL,
    
    -- 純資産の部
    total_equity REAL,
    capital_stock REAL,
    retained_earnings REAL,
    
    data_source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, fiscal_year, quarter)
);

-- 損益計算書 (PL)
CREATE TABLE income_statements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    quarter INTEGER,
    report_date TEXT NOT NULL,
    
    -- 売上
    revenue REAL,
    operating_revenue REAL, -- 電力事業特有
    
    -- 費用
    cost_of_sales REAL,
    selling_general_admin REAL,
    fuel_cost REAL, -- 電力業界重要指標
    
    -- 利益
    operating_income REAL,
    ordinary_income REAL,
    net_income REAL,
    ebitda REAL,
    
    data_source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, fiscal_year, quarter)
);

-- キャッシュフロー計算書
CREATE TABLE cash_flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    quarter INTEGER,
    report_date TEXT NOT NULL,
    
    operating_cf REAL,
    investing_cf REAL,
    financing_cf REAL,
    free_cash_flow REAL,
    
    data_source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, fiscal_year, quarter)
);

-- 株価情報
CREATE TABLE stock_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    adjusted_close REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, date)
);

-- 財務指標 (計算済み)
CREATE TABLE financial_ratios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    quarter INTEGER,
    calc_date TEXT NOT NULL,
    
    -- 収益性指標
    roe REAL, -- 自己資本利益率
    roa REAL, -- 総資産利益率
    operating_margin REAL, -- 営業利益率
    net_margin REAL, -- 純利益率
    
    -- 安全性指標
    current_ratio REAL, -- 流動比率
    debt_equity_ratio REAL, -- 負債資本比率
    equity_ratio REAL, -- 自己資本比率
    interest_coverage REAL, -- インタレストカバレッジ
    
    -- 効率性指標
    total_asset_turnover REAL, -- 総資産回転率
    
    -- 成長性指標
    revenue_growth_rate REAL,
    net_income_growth_rate REAL,
    
    -- 株価指標 (上場企業のみ)
    per REAL, -- 株価収益率
    pbr REAL, -- 株価純資産倍率
    dividend_yield REAL, -- 配当利回り
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, fiscal_year, quarter)
);

-- 電力業界特有指標
CREATE TABLE power_industry_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id TEXT NOT NULL,
    date TEXT NOT NULL,
    
    -- 販売電力量 (MWh)
    retail_sales_volume REAL,
    wholesale_sales_volume REAL,
    
    -- 発電設備容量 (MW)
    thermal_capacity REAL,
    renewable_capacity REAL,
    nuclear_capacity REAL,
    
    -- 設備利用率
    capacity_factor REAL,
    
    -- 顧客数
    customer_count INTEGER,
    
    data_source TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE(company_id, date)
);

-- 市場環境指標
CREATE TABLE market_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    
    -- 電力市場
    jepx_spot_price REAL, -- JEPX スポット価格 (円/kWh)
    system_demand REAL, -- 電力需要 (MWh)
    
    -- 燃料価格
    lng_price REAL, -- LNG価格 ($/MMBtu)
    coal_price REAL, -- 石炭価格 ($/ton)
    crude_oil_price REAL, -- 原油価格 ($/barrel)
    
    -- 為替
    usd_jpy_rate REAL,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 分析アラート履歴
CREATE TABLE analysis_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_date TEXT NOT NULL,
    company_id TEXT,
    alert_type TEXT NOT NULL, -- 'financial', 'market', 'ratio'
    severity TEXT NOT NULL, -- 'info', 'warning', 'critical'
    title TEXT NOT NULL,
    description TEXT,
    metric_name TEXT,
    metric_value REAL,
    threshold_value REAL,
    github_issue_number INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(company_id)
);

-- インデックス作成
CREATE INDEX idx_bs_company_year ON balance_sheets(company_id, fiscal_year);
CREATE INDEX idx_is_company_year ON income_statements(company_id, fiscal_year);
CREATE INDEX idx_cf_company_year ON cash_flows(company_id, fiscal_year);
CREATE INDEX idx_stock_company_date ON stock_prices(company_id, date);
CREATE INDEX idx_ratios_company_year ON financial_ratios(company_id, fiscal_year);
CREATE INDEX idx_power_company_date ON power_industry_metrics(company_id, date);
CREATE INDEX idx_market_date ON market_indicators(date);
CREATE INDEX idx_alerts_date ON analysis_alerts(alert_date);
```

---

## 5. GitHub Actions 実装仕様

### 5.1 ワークフロー設定

yaml

```yaml
# .github/workflows/daily-update.yml
name: Daily Data Update

on:
  schedule:
    # 毎日 18:00 JST (9:00 UTC) に実行
    - cron: "0 9 * * *"
  workflow_dispatch: # 手動実行も可能

permissions:
  contents: write
  issues: write
  pages: write

env:
  DB_FILE: data/power.db
  RAW_DATA_DIR: data/raw

jobs:
  update-database:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          # requests, pandas, beautifulsoup4, lxml, sqlite3
      
      - name: Download existing database
        run: |
          mkdir -p data
          if [ -f "${{ env.DB_FILE }}" ]; then
            echo "Database exists"
          else
            python scripts/init_database.py
          fi
      
      - name: Get latest data date from DB
        id: get_date
        run: |
          LAST_DATE=$(python scripts/get_last_update_date.py)
          echo "last_date=$LAST_DATE" >> $GITHUB_OUTPUT
      
      - name: Fetch stock prices
        run: |
          python scripts/fetch_stock_prices.py \
            --start-date "${{ steps.get_date.outputs.last_date }}"
        continue-on-error: true
      
      - name: Fetch EDINET reports
        run: |
          python scripts/fetch_edinet_reports.py
        continue-on-error: true
      
      - name: Fetch market indicators
        run: |
          python scripts/fetch_market_indicators.py \
            --start-date "${{ steps.get_date.outputs.last_date }}"
        continue-on-error: true
      
      - name: Parse and normalize data
        run: |
          python scripts/parse_financial_data.py
          python scripts/calculate_ratios.py
      
      - name: Run analysis
        id: analysis
        run: |
          python scripts/run_analysis.py > analysis_output.txt
          echo "analysis_file=analysis_output.txt" >> $GITHUB_OUTPUT
      
      - name: Create GitHub Issue for alerts
        if: success()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const analysis = fs.readFileSync('analysis_output.txt', 'utf8');
            
            if (analysis.includes('ALERT')) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `📊 Daily Analysis Alert - ${new Date().toISOString().split('T')[0]}`,
                body: `## 自動分析結果\n\n\`\`\`\n${analysis}\n\`\`\`\n\n---\n*Generated by GitHub Actions*`,
                labels: ['auto-analysis', 'daily-report']
              });
            }
      
      - name: Generate presigned URL for SQLite
        id: generate_url
        run: |
          # GitHub Release または Artifacts を使用
          DB_URL="https://github.com/${{ github.repository }}/raw/main/${{ env.DB_FILE }}"
          echo "db_url=$DB_URL" >> $GITHUB_OUTPUT
      
      - name: Update GitHub Pages
        run: |
          python scripts/generate_dashboard_html.py \
            --db-url "${{ steps.generate_url.outputs.db_url }}"
      
      - name: Commit and push changes
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add data/ docs/
          git diff --quiet && git diff --staged --quiet || \
            git commit -m "chore: daily data update $(date +'%Y-%m-%d')"
          git push
      
      - name: Create job summary
        run: |
          echo "## 📈 Daily Update Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "- **Database**: [${{ env.DB_FILE }}](${{ steps.generate_url.outputs.db_url }})" >> $GITHUB_STEP_SUMMARY
          echo "- **Dashboard**: [View Dashboard](https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }})" >> $GITHUB_STEP_SUMMARY
          echo "- **Last Update**: $(date)" >> $GITHUB_STEP_SUMMARY
          python scripts/generate_summary_stats.py >> $GITHUB_STEP_SUMMARY
```

### 5.2 データ欠損防止策

python

````python
# scripts/get_last_update_date.py
import sqlite3
from datetime import datetime, timedelta

def get_last_update_date(db_path='data/power.db'):
    """DB内の最新データ日付を取得"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 各テーブルの最新日付を取得
        cursor.execute("""
            SELECT MAX(date) FROM stock_prices
            UNION ALL
            SELECT MAX(date) FROM market_indicators
        """)
        
        dates = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        
        if dates:
            latest = max(dates)
            # 1日前から取得して重複を防ぐ
            return (datetime.fromisoformat(latest) - timedelta(days=1)).date()
        else:
            # 初回は30日前から
            return (datetime.now() - timedelta(days=30)).date()
    except:
        return (datetime.now() - timedelta(days=30)).date()
```

---

## 6. ダッシュボード機能仕様

### 6.1 表示カード一覧

#### 6.1.1 財務健全性カード
**指標**:
- 自己資本比率 (目安: 30%以上が健全)
- 負債資本比率 (D/Eレシオ)
- 流動比率
- インタレストカバレッジ

**グラフ**:
- 5年間の推移 (折れ線グラフ)
- 3社比較 (棒グラフ)

**解説例**:
> 東京電力の自己資本比率は15.2%と業界平均を下回っています。福島第一原発事故後の賠償・廃炉費用が影響していますが、2022年度から改善傾向にあります。

#### 6.1.2 収益性カード
**指標**:
- ROE (自己資本利益率)
- ROA (総資産利益率)
- 営業利益率
- 純利益率

**グラフ**:
- 四半期ごとの推移
- 業界ベンチマーク比較

#### 6.1.3 株価パフォーマンスカード (東電・中部電のみ)
**指標**:
- 株価推移 (1年/3年/5年)
- PER / PBR
- 配当利回り
- ベータ値 (TOPIX比)

**グラフ**:
- ローソク足チャート
- 移動平均線 (25日/75日/200日)

#### 6.1.4 燃料コスト感応度カード
**指標**:
- 燃料費比率 (売上高に対する%)
- LNG価格との相関係数
- 為替感応度

**グラフ**:
- 燃料費推移 vs 燃料価格推移
- ヒートマップ (感応度マトリクス)

#### 6.1.5 電力販売動向カード
**指標**:
- 販売電力量 (前年同期比)
- 市場シェア
- 顧客数推移

**グラフ**:
- 月次販売量推移
- セグメント別内訳 (円グラフ)

#### 6.1.6 市場環境カード
**指標**:
- JEPX平均価格
- 電力需要
- 稼働率

**グラフ**:
- 電力需給バランス
- 価格変動率

#### 6.1.7 ESG・脱炭素カード
**指標**:
- 再エネ比率
- CO2排出量
- 設備投資額 (脱炭素関連)

**グラフ**:
- 電源構成推移
- 脱炭素ロードマップ進捗

#### 6.1.8 アラート・異常検知カード
**表示内容**:
- 前日比大幅変動
- 閾値超過アラート
- 異常パターン検出

---

## 7. フロントエンド実装仕様

### 7.1 技術スタック
- **HTML5 + CSS3**
- **JavaScript (Vanilla)** または **React** (軽量版)
- **SQL.js**: ブラウザ内SQLite実行
- **Chart.js**: グラフ描画
- **TailwindCSS**: スタイリング

### 7.2 ファイル構成
```
docs/
├── index.html          # メインダッシュボード
├── css/
│   └── dashboard.css
├── js/
│   ├── main.js        # エントリーポイント
│   ├── db-loader.js   # SQLiteローダー
│   ├── chart-utils.js # グラフ生成
│   └── analysis.js    # 分析ロジック
└── assets/
    └── logo/
````

### 7.3 SQLite自動ロード実装例

javascript

```javascript
// js/db-loader.js
import initSqlJs from 'https://cdn.jsdelivr.net/npm/sql.js@1.8.0/+esm';

class DatabaseLoader {
  constructor() {
    this.db = null;
    this.SQL = null;
  }

  async initialize(dbUrl) {
    // URLパラメータからDB URLを取得
    const params = new URLSearchParams(window.location.search);
    const sourceUrl = params.get('db') || dbUrl;

    // キャッシュチェック
    const cachedDb = localStorage.getItem('power_db_cache');
    const cacheTime = localStorage.getItem('power_db_cache_time');
    const now = Date.now();

    if (cachedDb && cacheTime && (now - parseInt(cacheTime)) < 86400000) {
      // 24時間以内のキャッシュがあれば使用
      await this.loadFromCache(cachedDb);
      return;
    }

    // 新規ダウンロード
    try {
      const response = await fetch(sourceUrl);
      const arrayBuffer = await response.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);

      // キャッシュに保存
      const base64 = btoa(String.fromCharCode.apply(null, uint8Array));
      localStorage.setItem('power_db_cache', base64);
      localStorage.setItem('power_db_cache_time', now.toString());

      await this.loadDatabase(uint8Array);
    } catch (error) {
      console.error('Failed to load database:', error);
      throw error;
    }
  }

  async loadFromCache(base64Data) {
    const binaryString = atob(base64Data);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    await this.loadDatabase(bytes);
  }

  async loadDatabase(uint8Array) {
    this.SQL = await initSqlJs({
      locateFile: file => `https://cdn.jsdelivr.net/npm/sql.js@1.8.0/dist/${file}`
    });
    this.db = new this.SQL.Database(uint8Array);
  }

  query(sql, params = []) {
    if (!this.db) throw new Error('Database not initialized');
    const stmt = this.db.prepare(sql);
    stmt.bind(params);
    
    const results = [];
    while (stmt.step()) {
      results.push(stmt.getAsObject());
    }
    stmt.free();
    return results;
  }

  close() {
    if (this.db) {
      this.db.close();
    }
  }
}

export default DatabaseLoader;
```

### 7.4 ダッシュボードレイアウト

html

```html
<!-- index.html (簡略版) -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>電力3社 経営分析ダッシュボード</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
</head>
<body class="bg-gray-100">
  <div class="container mx-auto p-4">
    <header class="mb-8">
      <h1 class="text-3xl font-bold">⚡ 電力3社 経営分析ダッシュボード</h1>
      <p class="text-gray-600">東京電力 | 中部電力 | JERA</p>
      <div id="last-update" class="text-sm text-gray-500"></div>
    </header>

    <!-- フィルター -->
    <div class="mb-4 flex gap-4">
      <select id="company-filter" class="border p-2 rounded">
        <option value="all">全社表示</option>
        <option value="tepco">東京電力</option>
        <option value="chuden">中部電力</option>
        <option value="jera">JERA</option>
      </select>
      
      <select id="period-filter" class="border p-2 rounded">
        <option value="1y">1年</option>
        <option value="3y">3年</option>
        <option value="5y">5年</option>
      </select>
    </div>

    <!-- ダッシュボードグリッド -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- カード1: 財務健全性 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">📊 財務健全性</h2>
        <canvas id="chart-solvency"></canvas>
        <div id="analysis-solvency" class="mt-4 text-sm text-gray-700"></div>
      </div>

      <!-- カード2: 収益性 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">💰 収益性指標</h2>
        <canvas id="chart-profitability"></canvas>
        <div id="analysis-profitability" class="mt-4 text-sm text-gray-700"></div>
      </div>

      <!-- カード3: 株価 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">📈 株価推移</h2>
        <canvas id="chart-stock"></canvas>
        <div id="analysis-stock" class="mt-4 text-sm text-gray-700"></div>
      </div>

      <!-- カード4: 燃料コスト -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">⛽ 燃料コスト</h2>
        <canvas id="chart-fuel"></canvas>
        <div id="analysis-fuel" class="mt-4 text-sm text-gray-700"></div>
      </div>

      <!-- カード5: 販売動向 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">⚡ 販売電力量</h2>
        <canvas id="chart-sales"></canvas>
        <div id="analysis-sales" class="mt-4 text-sm text-gray-700"></div>
      </div>

      <!-- カード6: アラート -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">🚨 アラート</h2>
        <div id="alerts-list"></div>
      </div>
    </div>
  </div>

  <script type="module" src="js/main.js"></script>
</body>
</html>
```

---

## 8. 分析ロジック仕様

### 8.1 アラート検知ルール

python

```python
# scripts/run_analysis.py
```

再試行

HH

続ける

python

```python
# scripts/run_analysis.py (続き)

import sqlite3
from datetime import datetime, timedelta
import json

class FinancialAnalyzer:
    def __init__(self, db_path='data/power.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.alerts = []
    
    def run_all_checks(self):
        """全ての分析チェックを実行"""
        print("=" * 60)
        print(f"📊 Daily Financial Analysis - {datetime.now().strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        self.check_equity_ratio()
        self.check_profitability()
        self.check_stock_volatility()
        self.check_debt_level()
        self.check_fuel_cost_impact()
        self.check_quarterly_comparison()
        
        self.save_alerts()
        self.print_summary()
        
        return len([a for a in self.alerts if a['severity'] in ['warning', 'critical']]) > 0
    
    def check_equity_ratio(self):
        """自己資本比率のチェック"""
        query = """
        SELECT c.company_name, fr.equity_ratio, fr.fiscal_year, fr.quarter
        FROM financial_ratios fr
        JOIN companies c ON fr.company_id = c.company_id
        WHERE fr.equity_ratio IS NOT NULL
        ORDER BY fr.fiscal_year DESC, fr.quarter DESC
        LIMIT 3
        """
        
        results = self.conn.execute(query).fetchall()
        
        for row in results:
            ratio = row['equity_ratio']
            company = row['company_name']
            
            if ratio < 15:
                self.add_alert(
                    company_id=company,
                    alert_type='financial',
                    severity='critical',
                    title=f'自己資本比率が危険水準: {company}',
                    description=f'自己資本比率が{ratio:.1f}%と15%を下回っています。',
                    metric_name='equity_ratio',
                    metric_value=ratio,
                    threshold_value=15
                )
            elif ratio < 20:
                self.add_alert(
                    company_id=company,
                    alert_type='financial',
                    severity='warning',
                    title=f'自己資本比率が低水準: {company}',
                    description=f'自己資本比率が{ratio:.1f}%と20%を下回っています。',
                    metric_name='equity_ratio',
                    metric_value=ratio,
                    threshold_value=20
                )
    
    def check_profitability(self):
        """収益性指標のチェック"""
        query = """
        SELECT 
            c.company_name,
            fr.roe,
            fr.operating_margin,
            fr.net_margin,
            fr.fiscal_year,
            fr.quarter
        FROM financial_ratios fr
        JOIN companies c ON fr.company_id = c.company_id
        WHERE fr.fiscal_year >= (SELECT MAX(fiscal_year) FROM financial_ratios) - 1
        ORDER BY c.company_name, fr.fiscal_year DESC, fr.quarter DESC
        """
        
        results = self.conn.execute(query).fetchall()
        companies = {}
        
        for row in results:
            name = row['company_name']
            if name not in companies:
                companies[name] = []
            companies[name].append(row)
        
        for company, records in companies.items():
            if len(records) >= 2:
                current = records[0]
                previous = records[1]
                
                # ROEの大幅悪化チェック
                if current['roe'] and previous['roe']:
                    roe_change = current['roe'] - previous['roe']
                    if roe_change < -5:
                        self.add_alert(
                            company_id=company,
                            alert_type='financial',
                            severity='warning',
                            title=f'ROE大幅低下: {company}',
                            description=f'ROEが前期比{abs(roe_change):.1f}pt低下({previous["roe"]:.1f}% → {current["roe"]:.1f}%)',
                            metric_name='roe',
                            metric_value=current['roe'],
                            threshold_value=previous['roe']
                        )
                
                # 営業利益率の悪化チェック
                if current['operating_margin'] and previous['operating_margin']:
                    margin_change = current['operating_margin'] - previous['operating_margin']
                    if margin_change < -3:
                        self.add_alert(
                            company_id=company,
                            alert_type='financial',
                            severity='warning',
                            title=f'営業利益率低下: {company}',
                            description=f'営業利益率が前期比{abs(margin_change):.1f}pt低下',
                            metric_name='operating_margin',
                            metric_value=current['operating_margin'],
                            threshold_value=previous['operating_margin']
                        )
    
    def check_stock_volatility(self):
        """株価変動のチェック"""
        query = """
        SELECT 
            c.company_name,
            sp.date,
            sp.close,
            sp.volume,
            LAG(sp.close, 1) OVER (PARTITION BY c.company_id ORDER BY sp.date) as prev_close
        FROM stock_prices sp
        JOIN companies c ON sp.company_id = c.company_id
        WHERE sp.date >= date('now', '-7 days')
        AND c.securities_code IS NOT NULL
        ORDER BY c.company_name, sp.date DESC
        """
        
        results = self.conn.execute(query).fetchall()
        
        for row in results:
            if row['prev_close']:
                change_pct = ((row['close'] - row['prev_close']) / row['prev_close']) * 100
                
                if abs(change_pct) > 5:
                    severity = 'critical' if abs(change_pct) > 10 else 'warning'
                    direction = '急騰' if change_pct > 0 else '急落'
                    
                    self.add_alert(
                        company_id=row['company_name'],
                        alert_type='market',
                        severity=severity,
                        title=f'株価{direction}: {row["company_name"]}',
                        description=f'前日比{change_pct:+.2f}%の変動 ({row["prev_close"]:.0f}円 → {row["close"]:.0f}円)',
                        metric_name='stock_price_change',
                        metric_value=change_pct,
                        threshold_value=5
                    )
    
    def check_debt_level(self):
        """負債水準のチェック"""
        query = """
        SELECT 
            c.company_name,
            bs.total_liabilities,
            bs.total_equity,
            bs.long_term_debt,
            (bs.total_liabilities * 1.0 / NULLIF(bs.total_equity, 0)) as debt_equity_ratio
        FROM balance_sheets bs
        JOIN companies c ON bs.company_id = c.company_id
        WHERE bs.fiscal_year = (SELECT MAX(fiscal_year) FROM balance_sheets)
        AND bs.quarter IS NULL  -- 年次データのみ
        """
        
        results = self.conn.execute(query).fetchall()
        
        for row in results:
            de_ratio = row['debt_equity_ratio']
            if de_ratio and de_ratio > 2.0:
                self.add_alert(
                    company_id=row['company_name'],
                    alert_type='financial',
                    severity='warning',
                    title=f'負債比率高水準: {row["company_name"]}',
                    description=f'D/Eレシオが{de_ratio:.2f}倍と高水準です。',
                    metric_name='debt_equity_ratio',
                    metric_value=de_ratio,
                    threshold_value=2.0
                )
    
    def check_fuel_cost_impact(self):
        """燃料費影響のチェック"""
        query = """
        SELECT 
            date,
            lng_price,
            crude_oil_price,
            LAG(lng_price, 30) OVER (ORDER BY date) as lng_30d_ago,
            LAG(crude_oil_price, 30) OVER (ORDER BY date) as oil_30d_ago
        FROM market_indicators
        WHERE date >= date('now', '-31 days')
        ORDER BY date DESC
        LIMIT 1
        """
        
        result = self.conn.execute(query).fetchone()
        
        if result and result['lng_30d_ago']:
            lng_change = ((result['lng_price'] - result['lng_30d_ago']) / result['lng_30d_ago']) * 100
            
            if abs(lng_change) > 15:
                severity = 'warning' if abs(lng_change) < 25 else 'critical'
                direction = '急騰' if lng_change > 0 else '急落'
                
                self.add_alert(
                    company_id='全社',
                    alert_type='market',
                    severity=severity,
                    title=f'LNG価格{direction}',
                    description=f'LNG価格が30日前比{lng_change:+.1f}%変動。燃料費への影響に注意。',
                    metric_name='lng_price_change',
                    metric_value=lng_change,
                    threshold_value=15
                )
    
    def check_quarterly_comparison(self):
        """四半期比較"""
        query = """
        SELECT 
            c.company_name,
            i.fiscal_year,
            i.quarter,
            i.revenue,
            i.operating_income,
            i.net_income,
            LAG(i.revenue, 1) OVER (PARTITION BY c.company_id ORDER BY i.fiscal_year, i.quarter) as prev_revenue
        FROM income_statements i
        JOIN companies c ON i.company_id = c.company_id
        WHERE i.quarter IS NOT NULL
        ORDER BY c.company_name, i.fiscal_year DESC, i.quarter DESC
        LIMIT 9  -- 3社 × 最新3四半期
        """
        
        results = self.conn.execute(query).fetchall()
        
        for row in results:
            if row['prev_revenue'] and row['revenue']:
                revenue_change = ((row['revenue'] - row['prev_revenue']) / row['prev_revenue']) * 100
                
                if revenue_change < -10:
                    self.add_alert(
                        company_id=row['company_name'],
                        alert_type='financial',
                        severity='warning',
                        title=f'売上高大幅減少: {row["company_name"]}',
                        description=f'Q{row["quarter"]} 売上高が前期比{revenue_change:.1f}%減少',
                        metric_name='revenue_change',
                        metric_value=revenue_change,
                        threshold_value=-10
                    )
    
    def add_alert(self, company_id, alert_type, severity, title, description, 
                  metric_name=None, metric_value=None, threshold_value=None):
        """アラートを追加"""
        alert = {
            'company_id': company_id,
            'alert_type': alert_type,
            'severity': severity,
            'title': title,
            'description': description,
            'metric_name': metric_name,
            'metric_value': metric_value,
            'threshold_value': threshold_value
        }
        self.alerts.append(alert)
        
        # コンソール出力
        emoji = '🔴' if severity == 'critical' else '⚠️' if severity == 'warning' else 'ℹ️'
        print(f"\n{emoji} [{severity.upper()}] {title}")
        print(f"   {description}")
    
    def save_alerts(self):
        """アラートをDBに保存"""
        cursor = self.conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        for alert in self.alerts:
            cursor.execute("""
                INSERT INTO analysis_alerts 
                (alert_date, company_id, alert_type, severity, title, description,
                 metric_name, metric_value, threshold_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                today,
                alert['company_id'],
                alert['alert_type'],
                alert['severity'],
                alert['title'],
                alert['description'],
                alert['metric_name'],
                alert['metric_value'],
                alert['threshold_value']
            ))
        
        self.conn.commit()
    
    def print_summary(self):
        """サマリーを出力"""
        print("\n" + "=" * 60)
        print("📋 Analysis Summary")
        print("=" * 60)
        
        critical = len([a for a in self.alerts if a['severity'] == 'critical'])
        warning = len([a for a in self.alerts if a['severity'] == 'warning'])
        info = len([a for a in self.alerts if a['severity'] == 'info'])
        
        print(f"🔴 Critical: {critical}")
        print(f"⚠️  Warning:  {warning}")
        print(f"ℹ️  Info:     {info}")
        print(f"📊 Total:    {len(self.alerts)}")
        
        if critical > 0 or warning > 0:
            print("\n⚡ ALERT: 重要な問題が検出されました")
        else:
            print("\n✅ OK: 重大な問題は検出されませんでした")
        
        print("=" * 60)
    
    def close(self):
        self.conn.close()


if __name__ == '__main__':
    analyzer = FinancialAnalyzer()
    has_alerts = analyzer.run_all_checks()
    analyzer.close()
    
    # GitHub Actionsのexit codeに反映
    exit(1 if has_alerts else 0)
```

---

## 9. データ収集スクリプト仕様

### 9.1 EDINET APIクライアント

python

```python
# scripts/fetch_edinet_reports.py

import requests
import sqlite3
import json
from datetime import datetime, timedelta
import time
import os

class EdinetClient:
    BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"
    
    # 対象企業のEDINETコード
    TARGET_COMPANIES = {
        'E04498': 'tepco',    # 東京電力HD
        'E04285': 'chuden',   # 中部電力
        'E36542': 'jera'      # JERA
    }
    
    def __init__(self, subscription_key=None):
        self.subscription_key = subscription_key or os.getenv('EDINET_API_KEY')
        self.session = requests.Session()
        if self.subscription_key:
            self.session.headers.update({
                'Ocp-Apim-Subscription-Key': self.subscription_key
            })
    
    def get_document_list(self, date):
        """指定日の書類一覧を取得"""
        url = f"{self.BASE_URL}/documents.json"
        params = {
            'date': date.strftime('%Y-%m-%d'),
            'type': 2  # 2: メタデータのみ
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def download_xbrl(self, doc_id, save_dir='data/raw/edinet'):
        """XBRLファイルをダウンロード"""
        url = f"{self.BASE_URL}/documents/{doc_id}"
        params = {'type': 1}  # 1: 提出書類一式
        
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{doc_id}.zip")
        
        response = self.session.get(url, params=params, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return save_path
    
    def fetch_recent_reports(self, days=7):
        """直近N日間の報告書を取得"""
        reports = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            
            try:
                doc_list = self.get_document_list(date)
                
                for doc in doc_list.get('results', []):
                    edinet_code = doc.get('edinetCode')
                    doc_type = doc.get('docTypeCode')
                    
                    # 対象企業 & 有価証券報告書/四半期報告書
                    if (edinet_code in self.TARGET_COMPANIES and 
                        doc_type in ['120', '130', '140']):  # 有報、半期、四半期
                        
                        reports.append({
                            'doc_id': doc['docID'],
                            'company_id': self.TARGET_COMPANIES[edinet_code],
                            'edinet_code': edinet_code,
                            'doc_type': doc_type,
                            'doc_type_name': doc.get('docDescription'),
                            'submit_date': doc.get('submitDateTime'),
                            'fiscal_year': doc.get('periodEnd', '')[:4] if doc.get('periodEnd') else None
                        })
                
                time.sleep(1)  # レート制限対策
                
            except Exception as e:
                print(f"Error fetching {date}: {e}")
                continue
        
        return reports
    
    def save_to_database(self, reports, db_path='data/power.db'):
        """報告書情報をDBに保存"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # メタデータテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edinet_documents (
                doc_id TEXT PRIMARY KEY,
                company_id TEXT NOT NULL,
                edinet_code TEXT,
                doc_type TEXT,
                doc_type_name TEXT,
                submit_date TEXT,
                fiscal_year INTEGER,
                downloaded BOOLEAN DEFAULT 0,
                parsed BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        for report in reports:
            cursor.execute("""
                INSERT OR IGNORE INTO edinet_documents
                (doc_id, company_id, edinet_code, doc_type, doc_type_name, 
                 submit_date, fiscal_year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                report['doc_id'],
                report['company_id'],
                report['edinet_code'],
                report['doc_type'],
                report['doc_type_name'],
                report['submit_date'],
                report['fiscal_year']
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Saved {len(reports)} EDINET reports to database")


def main():
    client = EdinetClient()
    
    print("🔍 Fetching EDINET reports...")
    reports = client.fetch_recent_reports(days=30)
    
    print(f"📄 Found {len(reports)} relevant reports")
    
    if reports:
        client.save_to_database(reports)
        
        # 新規報告書のダウンロード
        for report in reports[:5]:  # 最新5件のみダウンロード
            try:
                print(f"⬇️  Downloading {report['doc_id']}...")
                client.download_xbrl(report['doc_id'])
                time.sleep(2)
            except Exception as e:
                print(f"❌ Failed: {e}")


if __name__ == '__main__':
    main()
```

### 9.2 株価取得スクリプト

python

```python
# scripts/fetch_stock_prices.py

import requests
import sqlite3
from datetime import datetime, timedelta
import time
import argparse

class StockPriceFetcher:
    # Yahoo Finance APIの代替として yfinance を使用
    SECURITIES_CODES = {
        'tepco': '9501.T',
        'chuden': '9502.T'
    }
    
    def __init__(self, db_path='data/power.db'):
        self.db_path = db_path
    
    def fetch_prices(self, symbol, start_date, end_date=None):
        """株価データを取得 (yfinance使用)"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(
                start=start_date,
                end=end_date or datetime.now(),
                interval='1d'
            )
            
            return hist
            
        except ImportError:
            print("⚠️  yfinance not installed. Please run: pip install yfinance")
            return None
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")
            return None
    
    def save_to_database(self, company_id, df):
        """株価データをDBに保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        count = 0
        for date, row in df.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO stock_prices
                (company_id, date, open, high, low, close, volume, adjusted_close)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                date.strftime('%Y-%m-%d'),
                row['Open'],
                row['High'],
                row['Low'],
                row['Close'],
                int(row['Volume']),
                row['Close']  # Adjusted close
            ))
            count += 1
        
        conn.commit()
        conn.close()
        
        return count
    
    def update_all_companies(self, start_date):
        """全社の株価を更新"""
        total_records = 0
        
        for company_id, symbol in self.SECURITIES_CODES.items():
            print(f"📊 Fetching {company_id} ({symbol})...")
            
            df = self.fetch_prices(symbol, start_date)
            
            if df is not None and not df.empty:
                count = self.save_to_database(company_id, df)
                total_records += count
                print(f"   ✅ Saved {count} records")
            
            time.sleep(1)  # レート制限対策
        
        print(f"\n✅ Total: {total_records} stock price records updated")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start-date', type=str, 
                       default=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    args = parser.parse_args()
    
    fetcher = StockPriceFetcher()
    fetcher.update_all_companies(args.start_date)


if __name__ == '__main__':
    main()
```

---

## 10. デプロイ手順

### 10.1 初期セットアップ

bash

```bash
# 1. リポジトリ作成
git init power-company-dashboard
cd power-company-dashboard

# 2. ディレクトリ構造作成
mkdir -p data/raw/{edinet,stock,market}
mkdir -p docs/{css,js,assets}
mkdir -p scripts
mkdir -p .github/workflows

# 3. 依存関係ファイル作成
cat > requirements.txt << EOF
requests==2.31.0
pandas==2.1.4
beautifulsoup4==4.12.2
lxml==4.9.3
yfinance==0.2.32
openpyxl==3.1.2
python-dateutil==2.8.2
EOF

# 4. 初期化スクリプト実行
python scripts/init_database.py

# 5. Git設定
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/power-company-dashboard.git
git push -u origin main

# 6. GitHub Pages有効化
# Settings > Pages > Source: GitHub Actions

# 7. Secrets設定 (必要に応じて)
# Settings > Secrets and variables > Actions
# - EDINET_API_KEY (optional)
```

### 10.2 手動初回実行

bash

```bash
# ローカルで初回データ収集
python scripts/fetch_stock_prices.py --start-date 2020-01-01
python scripts/fetch_edinet_reports.py
python scripts/fetch_market_indicators.py
python scripts/calculate_ratios.py

# DBをコミット
git add data/power.db
git commit -m "Add initial database"
git push
```

---

## 11. 監視・メンテナンス

### 11.1 日次チェック項目

- GitHub Actions の実行状態
- Issues に作成されたアラート
- データ更新の欠損チェック

### 11.2 月次メンテナンス

- SQLiteファイルサイズ確認 (100MB超えたら古いデータ削除)
- 生データファイルのクリーンアップ
- GitHub Storageの容量確認

### 11.3 トラブルシューティング

python

```python
# scripts/diagnose_database.py
import sqlite3

def diagnose():
    conn = sqlite3.connect('data/power.db')
    cursor = conn.cursor()
    
    print("📊 Database Diagnostics")
    print("=" * 50)
    
    # テーブルごとのレコード数
    tables = ['companies', 'balance_sheets', 'income_statements', 
              'stock_prices', 'financial_ratios', 'analysis_alerts']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table:25s}: {count:6d} records")
    
    # 最新データ日付
    cursor.execute("SELECT MAX(date) FROM stock_prices")
    latest_stock = cursor.fetchone()[0]
    print(f"\nLatest stock price: {latest_stock}")
    
    # データ欠損チェック
    cursor.execute("""
        SELECT DATE(date) as d
        FROM (
            SELECT date FROM stock_prices WHERE company_id = 'tepco'
            ORDER BY date DESC LIMIT 30
        )
    """)
    dates = [row[0] for row in cursor.fetchall()]
    print(f"Stock data coverage (last 30): {len(dates)} days")
    
    conn.close()

if __name__ == '__main__':
    diagnose()
```

---

## 12. 拡張機能候補

### 12.1 Phase 2 機能

- **AI解説生成**: Claude APIで財務分析レポート自動生成
- **比較分析**: 他電力会社 (関西電力、九州電力) 追加
- **予測モデル**: 機械学習による業績予測
- **Slack/Discord通知**: GitHub Issues以外の通知チャネル

### 12.2 Phase 3 機能

- **ユーザー認証**: パスワード保護されたプライベートダッシュボード
- **カスタムアラート**: ユーザー定義の閾値設定
- **エクスポート機能**: PDF/Excel形式でのレポート出力
- **リアルタイム更新**: WebSocket経由の自動リフレッシュ

---

## 13. コスト試算

|項目|月額コスト|
|---|---|
|GitHubリポジトリ (Public)|**¥0**|
|GitHub Actions (2,000分/月無料枠)|**¥0**|
|GitHub Pages (1GB/月無料)|**¥0**|
|外部API (無料枠内)|**¥0**|
|**合計**|**¥0**|

※ Private リポジトリの場合は GitHub Pro (月$4) が必要

---

## 14. FAQ

**Q: SQLiteファイルが大きくなりすぎた場合は?**  
A: 古いデータをアーカイブして別ファイルに分割するか、`VACUUM` コマンドで最適化

**Q: GitHub Actions が失敗した場合は?**  
A: 手動で `workflow_dispatch` を実行して再実行。エラーログを確認してスクリプト修正

**Q: ブラウザでSQLiteが読み込めない場合は?**  
A: sql.js のCDNが利用可能か確認。ローカルファイルを直接指定して動作確認

**Q: 非上場のJERAの財務データは?**  
A: EDINET経由で有価証券報告書相当の資料が取得可能

---

## 15. まとめ

本仕様書に基づき実装することで:

- ✅ **完全無料**のインフラで稼働
- ✅ **自動更新**による手間ゼロの運用
- ✅ **ブラウザ完結**のデータ分析
- ✅ **拡張性**の高いアーキテクチャ

を実現できます。

---

**作成日**: 2025年11月22日  
**バージョン**: 1.0  
**作成者**: AI Assistant