-- 株式分析システム データベーススキーマ
-- SQLite 3.x
-- 作成日: 2025-11-22

-- ============================================================
-- テーブル1: 企業情報
-- ============================================================
CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY,                  -- 証券コード（例: 9501）
    name TEXT NOT NULL,                   -- 企業名（例: 東京電力ホールディングス）
    market TEXT,                          -- 市場（例: 東証プライム）
    sector TEXT,                          -- セクター（例: 電気・ガス業）
    shares_outstanding INTEGER,           -- 発行済株式数
    market_cap REAL,                      -- 時価総額（円）
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- インデックス: 企業名検索用
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);

-- インデックス: セクター検索用
CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);

-- ============================================================
-- テーブル2: 財務データ
-- ============================================================
CREATE TABLE IF NOT EXISTS financials (
    company_id TEXT NOT NULL,             -- 企業ID（外部キー）
    filing_date TEXT NOT NULL,            -- 決算日（YYYY-MM-DD）
    cash REAL,                            -- 現金及び現金同等物（円）
    securities REAL,                      -- 有価証券（円）
    receivables REAL,                     -- 売掛金（円）
    inventory REAL,                       -- 棚卸資産（円）
    total_assets REAL,                    -- 総資産（円）
    liabilities REAL,                     -- 負債合計（円）
    revenue REAL,                         -- 売上高（円）
    net_income REAL,                      -- 純利益（円）
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (company_id, filing_date),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- インデックス: 企業ID + 決算日検索用（クリティカルパス）
CREATE INDEX IF NOT EXISTS idx_financials_company_date 
    ON financials(company_id, filing_date DESC);

-- インデックス: 決算日検索用（時系列分析）
CREATE INDEX IF NOT EXISTS idx_financials_filing_date 
    ON financials(filing_date DESC);

-- ============================================================
-- テーブル3: 株価データ
-- ============================================================
CREATE TABLE IF NOT EXISTS stock_prices (
    company_id TEXT NOT NULL,             -- 企業ID（外部キー）
    date TEXT NOT NULL,                   -- 日付（YYYY-MM-DD）
    open REAL,                            -- 始値（円）
    high REAL,                            -- 高値（円）
    low REAL,                             -- 安値（円）
    close REAL NOT NULL,                  -- 終値（円）
    volume INTEGER,                       -- 出来高
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (company_id, date),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- インデックス: 企業ID + 日付検索用（クリティカルパス）
CREATE INDEX IF NOT EXISTS idx_stock_prices_company_date 
    ON stock_prices(company_id, date DESC);

-- インデックス: 日付検索用（市場全体分析）
CREATE INDEX IF NOT EXISTS idx_stock_prices_date 
    ON stock_prices(date DESC);

-- ============================================================
-- テーブル4: 解析キャッシュ
-- ============================================================
CREATE TABLE IF NOT EXISTS analysis_cache (
    company_id TEXT NOT NULL,             -- 企業ID（外部キー）
    analysis_type TEXT NOT NULL,          -- 解析タイプ（netnet, oneil, market_top）
    calculated_at TEXT NOT NULL,          -- 計算日時
    netnet_pbr REAL,                      -- NetNetPBR
    oneil_eps_3y REAL,                    -- EPS成長率（3年）
    oneil_eps_5y REAL,                    -- EPS成長率（5年）
    oneil_rs REAL,                        -- リラティブストレングス
    market_top_count INTEGER,             -- 分配日カウント（25日間）
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (company_id, analysis_type, calculated_at),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- インデックス: 解析タイプ + NetNetPBR検索用（割安株検出）
CREATE INDEX IF NOT EXISTS idx_analysis_cache_netnet 
    ON analysis_cache(analysis_type, netnet_pbr) 
    WHERE analysis_type = 'netnet' AND netnet_pbr IS NOT NULL;

-- インデックス: 解析タイプ + RS検索用（オニールスクリーニング）
CREATE INDEX IF NOT EXISTS idx_analysis_cache_oneil 
    ON analysis_cache(analysis_type, oneil_rs) 
    WHERE analysis_type = 'oneil' AND oneil_rs IS NOT NULL;

-- ============================================================
-- テーブル5: TOPIXデータ
-- ============================================================
CREATE TABLE IF NOT EXISTS topix_data (
    date TEXT PRIMARY KEY,                -- 日付（YYYY-MM-DD）
    close REAL NOT NULL,                  -- 終値
    volume INTEGER,                       -- 出来高
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- インデックス: 日付検索用（時系列分析）
CREATE INDEX IF NOT EXISTS idx_topix_data_date 
    ON topix_data(date DESC);

-- ============================================================
-- テーブル6: 通知履歴
-- ============================================================
CREATE TABLE IF NOT EXISTS notification_history (
    entity_id TEXT NOT NULL,              -- エンティティID（企業IDまたは'market-top'）
    notification_type TEXT NOT NULL,      -- 通知タイプ（undervalued, market-top）
    created_at TEXT NOT NULL,             -- 作成日時（YYYY-MM-DD）
    issue_number INTEGER,                 -- GitHub Issue番号
    PRIMARY KEY (entity_id, notification_type, created_at)
);

-- インデックス: エンティティID + 通知タイプ検索用（重複チェック）
CREATE INDEX IF NOT EXISTS idx_notification_history_entity 
    ON notification_history(entity_id, notification_type, created_at DESC);

-- ============================================================
-- 初期データ投入: サンプル企業
-- ============================================================
INSERT OR IGNORE INTO companies (id, name, market, sector, shares_outstanding, market_cap) VALUES
('9501', '東京電力ホールディングス', '東証プライム', '電気・ガス業', 1600000000, 800000000000),
('9502', '中部電力', '東証プライム', '電気・ガス業', 1400000000, 1680000000000);

-- ============================================================
-- パフォーマンス最適化設定
-- ============================================================
-- WALモード有効化（並行アクセス性能向上）
PRAGMA journal_mode = WAL;

-- キャッシュサイズ設定（64MB）
PRAGMA cache_size = -64000;

-- 外部キー制約有効化
PRAGMA foreign_keys = ON;

-- 同期モード（NORMAL: バランス型）
PRAGMA synchronous = NORMAL;

-- 一時ストレージ（メモリ使用）
PRAGMA temp_store = MEMORY;
