// データベース読み込みモジュール
// SQLiteデータベースから解析結果を取得し、HTMLに表示

class DatabaseLoader {
    constructor(dbPath) {
        this.dbPath = dbPath;
        this.db = null;
    }

    async init() {
        try {
            // sqlite3.jsライブラリ読み込み（CDN経由）
            const SQL = await initSqlJs({
                locateFile: file => `https://sql.js.org/dist/${file}`
            });

            // データベースファイル読み込み
            const response = await fetch(this.dbPath);
            if (!response.ok) {
                throw new Error(`Failed to load database: ${response.statusText}`);
            }

            const buffer = await response.arrayBuffer();
            this.db = new SQL.Database(new Uint8Array(buffer));

            console.log('✓ Database loaded successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize database:', error);
            return false;
        }
    }

    // NetNet株ランキング取得
    getNetNetRanking(limit = 50) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        const query = `
            SELECT 
                c.id AS ticker,
                c.name,
                c.sector,
                ac.netnet_pbr,
                c.market_cap,
                ac.calculated_at
            FROM analysis_cache ac
            JOIN companies c ON ac.company_id = c.id
            WHERE ac.analysis_type = 'netnet'
                AND ac.netnet_pbr IS NOT NULL
            ORDER BY ac.netnet_pbr ASC
            LIMIT ?
        `;

        const stmt = this.db.prepare(query);
        stmt.bind([limit]);

        const results = [];
        while (stmt.step()) {
            const row = stmt.getAsObject();
            results.push(row);
        }
        stmt.free();

        return results;
    }

    // O'Neilランキング取得
    getONeilRanking(limit = 50) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        const query = `
            SELECT 
                c.id AS ticker,
                c.name,
                c.sector,
                ac.oneil_eps_3y,
                ac.oneil_eps_5y,
                ac.oneil_rs,
                ac.calculated_at
            FROM analysis_cache ac
            JOIN companies c ON ac.company_id = c.id
            WHERE ac.analysis_type = 'oneil'
                AND ac.oneil_eps_3y IS NOT NULL
            ORDER BY ac.oneil_rs DESC
            LIMIT ?
        `;

        const stmt = this.db.prepare(query);
        stmt.bind([limit]);

        const results = [];
        while (stmt.step()) {
            const row = stmt.getAsObject();
            results.push(row);
        }
        stmt.free();

        return results;
    }

    // マーケット天井検出状態取得
    getMarketTopStatus() {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        const query = `
            SELECT 
                market_top_count,
                calculated_at
            FROM analysis_cache
            WHERE company_id = 'market-top'
                AND analysis_type = 'market_top'
            ORDER BY calculated_at DESC
            LIMIT 1
        `;

        const result = this.db.exec(query);

        if (result.length === 0 || result[0].values.length === 0) {
            return null;
        }

        const [count, calculatedAt] = result[0].values[0];

        return {
            distribution_count: count,
            is_warning: count >= 5,
            calculated_at: calculatedAt
        };
    }

    // TOPIX最新データ取得
    getLatestTOPIX() {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        const query = `
            SELECT date, close, volume
            FROM topix_data
            ORDER BY date DESC
            LIMIT 1
        `;

        const result = this.db.exec(query);

        if (result.length === 0 || result[0].values.length === 0) {
            return null;
        }

        const [date, close, volume] = result[0].values[0];

        return { date, close, volume };
    }

    // 企業数取得
    getCompanyCount() {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        const query = `SELECT COUNT(*) FROM companies`;
        const result = this.db.exec(query);

        return result[0].values[0][0];
    }

    // 割安株数取得
    getUndervaluedCount() {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        const query = `
            SELECT COUNT(*)
            FROM analysis_cache
            WHERE analysis_type = 'netnet'
                AND netnet_pbr < 1.0
        `;

        const result = this.db.exec(query);

        return result[0].values[0][0];
    }

    // 株価データ取得（チャート用）
    getStockPrices(ticker, days = 90) {
        if (!this.db) {
            throw new Error('Database not initialized');
        }

        const query = `
            SELECT date, open, high, low, close, volume
            FROM stock_prices
            WHERE company_id = ?
            ORDER BY date DESC
            LIMIT ?
        `;

        const stmt = this.db.prepare(query);
        stmt.bind([ticker, days]);

        const results = [];
        while (stmt.step()) {
            const row = stmt.getAsObject();
            results.push(row);
        }
        stmt.free();

        return results.reverse(); // 古い順に並び替え
    }
}

// エクスポート
window.DatabaseLoader = DatabaseLoader;
