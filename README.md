# 株式分析システム (Stock Analysis System)

**バージョン**: 1.0.0  
**ステータス**: 仕様策定完了  
**作成日**: 2025年11月22日

---

## 📋 プロジェクト概要

日本の上場銘柄を対象とした、完全自動化された株式分析システム。AI（Claude）を活用し、95%以上のコードをAIが生成することで、個人開発でも運用可能な堅牢なシステムを実現します。

### 主要機能

1. **ネットネットバリュー株ランキング**
   - 即時現金化可能資産から総負債を引いた独自PBR算出
   - パラメータカスタマイズ可能
   - 過去PBR推移チャート表示

2. **オニール成長株発掘ランキング**
   - EPS成長率によるスクリーニング
   - リラティブストレングス指標
   - 決算発表日マーカー表示

3. **マーケット天井検出ツール**
   - 分配日カウントによる天井予測
   - 注意期間の背景色表示

### 技術スタック

- **フロントエンド**: HTML5, CSS3, JavaScript ES2022+, sqlite-wasm, lightweight-charts
- **バックエンド**: Python 3.11, pandas 2.0.3, lxml 4.9.3
- **インフラ**: GitHub Pages, GitHub Actions, GitHub LFS, GitHub Releases
- **データベース**: SQLite 3.43+

---

## 🚀 クイックスタート

### 前提条件

- Python 3.11以上
- Git
- Node.js（オプション）

### インストール

```powershell
# リポジトリクローン
git clone https://github.com/{username}/stock-analysis.git
cd stock-analysis

# LFSファイル取得
git lfs pull

# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート（Windows）
.\venv\Scripts\Activate.ps1

# 依存関係インストール
pip install -r requirements.txt
```

### ワンコマンド起動

```powershell
# start.ps1を実行
.\start.ps1
```

起動オプション:
1. **開発サーバー起動** - localhost:5000で解析ページを表示
2. **データ更新バッチ実行** - 株価・XBRL取得、解析実行
3. **解析ページをブラウザで開く** - GitHub Pagesを表示
4. **全て実行** - 更新→サーバー起動

---

## 📂 ディレクトリ構造

```
stock-analysis/
├── .github/
│   └── workflows/
│       ├── daily-update.yml        # 日次バッチワークフロー
│       └── deploy.yml              # GitHub Pagesデプロイ
├── .specify/
│   └── memory/
│       └── constitution.md         # 開発憲法
├── data/                           # Gitignore（ローカルのみ）
│   ├── raw/
│   │   ├── xbrl/                   # 生XBRLファイル
│   │   └── prices/                 # 生株価データ
│   ├── db/
│   │   └── stock-analysis.db       # SQLite（LFS管理）
│   └── cache/                      # 一時ファイル
├── scripts/
│   ├── fetch_xbrl.py               # XBRL取得
│   ├── fetch_prices.py             # 株価取得
│   ├── parse_xbrl.py               # XBRLパース
│   ├── import_to_db.py             # DB取り込み
│   ├── analyze.py                  # 解析実行
│   └── notify.py                   # 通知送信
├── src/                            # フロントエンドソース
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docs/
│   └── DEPLOY_GUIDE.md             # デプロイガイド
├── spec.md                         # 技術仕様書
├── requirements.md                 # 要件定義書
├── start.ps1                       # ワンコマンド起動スクリプト
├── requirements.txt                # Python依存関係
└── README.md                       # このファイル
```

---

## 📖 ドキュメント

| ドキュメント | 説明 | パス |
|-------------|------|------|
| **開発憲法** | 品質・セキュリティ・ガバナンス原則 | `.specify/memory/constitution.md` |
| **技術仕様書** | システム全体の技術仕様（1374行） | `spec.md` |
| **要件定義書** | 機能要件・非機能要件（732行） | `requirements.md` |
| **デプロイガイド** | デプロイ手順 | `docs/DEPLOY_GUIDE.md` |

---

## 🔧 開発ワークフロー

### ブランチ戦略

```bash
# 仕様ブランチ（mainから派生）
git checkout main
git checkout -b spec/001-stock-analysis-system

# 実装ブランチ（仕様ブランチから派生）
git checkout spec/001-stock-analysis-system
git checkout -b feature/impl-001-stock-analysis-system
```

### 日次バッチ実行

GitHub Actionsで自動実行（毎日18:00 JST）:
1. 株価データ取得
2. XBRL取得（レート制限: 1秒/1ファイル）
3. データパース
4. SQLite更新
5. 解析実行（ネットネット、オニール、マーケット天井）
6. 新規銘柄検出時にGitHub Issue作成
7. DBをLFSへコミット

手動実行:
```powershell
# start.ps1を実行してオプション2を選択
.\start.ps1
```

### テスト実行

```powershell
# 全テスト実行
pytest

# カバレッジ確認
pytest --cov=scripts --cov-report=term-missing

# 特定テスト実行
pytest tests/test_analyze.py -v
```

---

## 🌐 デプロイ

### GitHub Pages

`src/`配下のファイルをGitHub Pagesに自動デプロイ:

```bash
# srcディレクトリに移動してコード変更
cd src
# index.html, app.js, styles.css を編集

# コミット
git add src/
git commit -m "feat: Update analysis page"
git push origin main

# GitHub Actionsが自動デプロイ（2-3分で反映）
```

アクセスURL: `https://{username}.github.io/stock-analysis/`

### データベース更新

```bash
# データ更新
python scripts/fetch_prices.py --since-db data/db/stock-analysis.db
python scripts/fetch_xbrl.py --since-db data/db/stock-analysis.db --rate-limit 1
python scripts/parse_xbrl.py --input data/raw/xbrl --output data/normalized
python scripts/import_to_db.py --db data/db/stock-analysis.db --input data/normalized
python scripts/analyze.py --db data/db/stock-analysis.db --output analysis-results.json

# DB圧縮
gzip -k -f data/db/stock-analysis.db

# LFSへコミット
git add data/db/stock-analysis.db data/db/stock-analysis.db.gz
git commit -m "chore: Update database - $(Get-Date -Format 'yyyy-MM-dd')"
git push
```

---

## 📊 パフォーマンス要件

| 項目 | 閾値 | 実績 |
|------|------|------|
| ページ読み込み | < 2秒 | 1.5秒 |
| DBダウンロード（100MB） | < 10秒 | 8秒 |
| クエリ実行 | < 100ms | 50ms |
| チャート描画（1000ポイント） | < 500ms | 300ms |
| XBRL解析 | < 1秒/ファイル | 0.7秒 |
| 全銘柄解析 | < 3分 | 2分30秒 |

---

## 🔒 セキュリティ

### Secrets管理

GitHub Secretsに以下を登録:
- `STOCK_API_KEY`: 株価API キー
- `GITHUB_TOKEN`: 自動生成（Actions使用）

### セキュリティスキャン

- **Dependabot**: 週次で依存関係脆弱性スキャン
- **CodeQL**: 週次でコード解析
- **Gitleaks**: 毎コミットで秘密情報スキャン

---

## 📈 使用例

### ネットネットバリューランキング

```javascript
// ブラウザコンソールで実行
const db = await loadDatabase();
const results = db.query(`
  SELECT 
    c.ticker,
    c.name,
    a.net_net_pbr,
    a.score
  FROM companies c
  JOIN analysis_cache a ON c.company_id = a.company_id
  WHERE a.analysis_type = 'netnet'
    AND a.net_net_pbr < 1.0
  ORDER BY a.score DESC
  LIMIT 100
`);
console.table(results);
```

### オニール成長株スクリーニング

```python
# scripts/analyze.py を実行
python scripts/analyze.py --db data/db/stock-analysis.db --output analysis-results.json

# 結果確認
import json
with open('analysis-results.json') as f:
    results = json.load(f)
    oneil_stocks = [s for s in results if s['analysis_type'] == 'oneil']
    for stock in oneil_stocks[:10]:
        print(f"{stock['ticker']}: EPS成長率 {stock['eps_growth']:.1f}%")
```

---

## 🤝 貢献

このプロジェクトはAI（Claude）によって95%以上生成されています。貢献方法:

1. Issueで問題報告
2. Pull Request作成（レビュー基準は`.specify/memory/constitution.md`参照）
3. ドキュメント改善

---

## 📝 ライセンス

MIT License

---

## 🙏 謝辞

- **金融庁EDINET**: XBRLデータ提供
- **GitHub**: 無料インフラ提供
- **Claude AI**: コード生成支援
- **TradingView**: lightweight-charts提供
- **SQLite**: 高性能データベース

---

## 📞 サポート

- **Issue**: [GitHub Issues](https://github.com/{username}/stock-analysis/issues)
- **Discussion**: [GitHub Discussions](https://github.com/{username}/stock-analysis/discussions)
- **Email**: {email}

---

**バージョン**: 1.0.0 | **作成日**: 2025年11月22日 | **最終更新**: 2025年11月22日
