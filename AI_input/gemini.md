
# 東京電力・中部電力・JERA 経営分析ダッシュボード 仕様書

## 1. プロジェクト概要

本プロジェクトは、東京電力ホールディングス（TEPCO）、中部電力、および両社の燃料・火力発電事業を統合したJERAの3社を対象とした、AI駆動型の経営分析アプリケーションを構築することを目的とする。

インフラコストを極小化するため、GitHubエコシステムのみを使用した完全サーバーレス構成を採用する。

## 2. アーキテクチャ設計

### 2.1. 基本構成

- **データベース:** SQLite (`data.db`) 単一ファイルで管理。
    
- **ストレージ:** GitHub Repository (Git LFS推奨)。
    
- **バックエンド/バッチ:** GitHub Actions (Daily Cron)。
    
- **フロントエンド:** GitHub Pages (Static HTML + WASM SQLite)。
    
- **通知システム:** GitHub Issues & Email。
    

### 2.2. データフロー図

1. **収集:** GitHub Actionsが外部ソース(EDINET, 株価API等)からデータを取得。
    
2. **加工:** Pythonスクリプトがデータを正規化・要約し、SQLiteへUPSERT。
    
3. **保存:** SQLiteファイルをGitリポジトリへCommit & Push。
    
4. **配信:** GitHub Pagesがブラウザ上でSQLiteファイルをダウンロード。
    
5. **表示:** ブラウザ内の `sql.js` (WASM) がDBを展開し、SQLを実行してグラフ描画。
    

## 3. 監視対象と提案指標 (AI Proposal)

電力業界特有の構造とJERAの立ち位置（TEPCO/中部電力の持分法適用会社）を考慮し、以下の指標をカード形式で表示する。

### 3.1. 財務指標 (TEPCO & 中部電力)

- **株価指標:** 株価推移、PER (株価収益率)、PBR (株価純資産倍率)、配当利回り。
    
- **収益性:** 売上高営業利益率、ROE (自己資本利益率)。
    
- **安全性:** 自己資本比率、D/Eレシオ（有利子負債依存度）。
    
- **キャッシュフロー:** 営業CF、フリーCFの推移。
    

### 3.2. JERA特化指標 (TEPCO/中部電力への影響)

JERAは非上場だが日本の発電量の約3割を担うため、親会社への利益貢献度が最重要となる。

- **JERA純利益:** 親会社2社への取り込み利益の源泉。
    
- **燃料調達コスト:** LNG/石炭のスポット価格とJERAの調達価格の乖離（調達競争力）。
    
- **JERA貢献度:** 親会社の経常利益に対するJERA持分法投資損益の割合。
    

### 3.3. 業界特有の重要指標 (オペレーショナルデータ)

- **燃料費調整額推移:** 燃料価格変動の電気料金への転嫁状況（タイムラグによる損益影響）。
    
- **販売電力量:** 小売（低圧/高圧）の販売量推移。
    
- **脱炭素進捗:** 再生可能エネルギー比率、アンモニア・水素混焼率（JERAの重要施策）。
    

## 4. 機能要件

### 4.1. データ収集・更新バッチ (GitHub Actions)

- **スケジュール:** 毎日 18:00 JST (`cron: "0 9 * * *"`)
    
- **処理内容:**
    
    1. **Checkout:** リポジトリから最新の `data.db` を取得。
        
    2. **Fetch Data:**
        
        - 株価情報 (Yahoo Finance API等)
            
        - 財務情報 (EDINET API / XBRLパース)
            
        - IRニュース (各社WebサイトのスクレイピングまたはRSS)
            
    3. **Update DB:** 取得データをSQLiteに追記・更新。
        
    4. **Archive Raw Data:** 取得した生データ（JSON/CSV）を `raw_data/YYYY-MM-DD/` に保存。
        
    5. **Commit & Push:** 更新された `data.db` と生データをリポジトリにプッシュ。
        
    6. **Analyze & Notify:** 異常値検知（例：株価の急変動、赤字転落の発表）があれば Issue 作成。
        

### 4.2. 通知機能 (GitHub Issues)

- バッチ処理完了後、以下の条件で自動的にIssueを作成する。
    
    - **Title:** `[Daily Report] YYYY-MM-DD Analysis Result`
        
    - **Body:**
        
        - 主要指標のサマリー（Markdownテーブル）
            
        - 前日比で大きく変動した項目
            
        - AIによる簡易コメント（OpenAI API等を利用し、数値変動の背景を推測）
            
    - **Assignees:** リポジトリオーナー（これによりメール通知が飛ぶ）
        

### 4.3. フロントエンド (Dashboard)

- **技術スタック:** React or Vue.js (Single Page Application), sql.js (SQLite WASM), Chart.js / Recharts。
    
- **データロード:**
    
    - URLクエリパラメータで指定されたパス、またはデフォルトの `raw` ファイルURLからSQLiteバイナリをDL。
        
    - ブラウザのIndexedDB等にキャッシュし、通信量を削減。
        
- **UI構成:**
    
    - **Summary View:** 3社の最新ステータス比較カード。
        
    - **Detail View:** 各指標の時系列グラフ（月次/年次切り替え）。
        
    - **AI Insight:** 決算短信PDF等をLLMで要約したテキスト表示エリア。
        

## 5. データベース設計 (SQLite Schema)

```
-- 企業マスタ
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    code TEXT, -- 9501, 9502, JERA
    name TEXT
);

-- 財務・株価データ（時系列）
CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    date TEXT, -- YYYY-MM-DD
    metric_name TEXT, -- "stock_price", "net_income", "fuel_cost_adj"
    value REAL,
    unit TEXT,
    source TEXT, -- "EDINET", "Yahoo", "Prediction"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ニュース・要約テキスト
CREATE TABLE insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    date TEXT,
    title TEXT,
    content TEXT, -- AI要約またはニュース本文
    url TEXT
);
```

## 6. 開発・運用フロー

### 6.1. ローカル開発

1. GitHubリポジトリをClone。
    
2. ローカルの `data.db` を指定してフロントエンドサーバーを起動 (`npm run dev`)。
    
3. 解析ロジックやUIを追加・修正。
    

### 6.2. 本番運用 (CI/CD)

1. `main` ブランチへのプッシュでGitHub Pagesのビルド・デプロイが走る。
    
2. 日次バッチ (`data_update.yml`) がDBを更新し、自動でデータが最新化される。
    
3. データの欠損を防ぐため、バッチ処理では `git pull --rebase` 戦略を用いて競合を回避する。
    

## 7. 拡張性への考慮

- **Presigned URL対応:** リポジトリをPrivateにする場合、Actions内で AWS S3 等へアップロードしPresigned URLを発行、あるいはGitHub APIでArtifactのURLを取得し、Issueに記載するURLにトークンを含める実装へ切り替え可能。
    
- **カスタム解析:** ローカルにある任意のSQLiteファイルをブラウザにドラッグ＆ドロップして解析できる機能を実装し、開発時のデータ検証を容易にする。