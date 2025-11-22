# 株式分析システム (Stock Analysis System)

**バージョン**: 1.0.0  
**最終更新**: 2025年11月25日  
**対象企業**: 東京電力ホールディングス（9501）、中部電力（9502）、JERA（非上場）

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-success)](https://j1921604.github.io/stock-analysis/)

---

## 📖 概要

電力業界3社（東京電力・中部電力・JERA）に特化した財務・株価自動分析システム。  
GitHub中心アーキテクチャにより、サーバー運用コストゼロで継続的なデータ更新・分析を実現します。

### 主要機能

- ⚡ **電力3社財務ダッシュボード**: リアルタイム財務指標可視化
- 📊 **電力業界特化指標**: 燃料費調整額、JERA期ずれ影響、発電構成比率
- 🤖 **自動データ更新**: EDINET API + Yahoo Finance APIから日次自動収集
- 🚀 **GitHub Pages配信**: 静的サイトとして自動デプロイ
- 🔔 **異常検知通知**: 株価急変・ROE低下時にGitHub Issue自動作成

---

## 🎯 現在の実装状況

### Phase 1: 基盤構築 ✅ 完了

- [x] Pythonプロジェクト構造作成
- [x] Git LFS設定（SQLite管理）
- [x] 開発憲法v1.0.0策定
- [x] データベーススキーマ作成（schema.sql）
- [x] DB初期化スクリプト（scripts/init_db.py）
- [x] 3社データ登録（東京電力HD/中部電力/JERA）
- [x] テストスイート完備（41テスト全パス）

### Phase 2: データパイプライン 🔵 実装中

- [ ] T007-T012: データ収集・解析スクリプト
- [ ] T013-T016: データ格納・財務指標計算

### Phase 3-5: 未着手

Phase 3以降の詳細は [タスク定義書](https://github.com/J1921604/stock-analysis/blob/main/specs/feature/impl-001-stock-analysis-system/tasks.md) を参照してください。

---

## 🚀 クイックスタート

### 前提条件

- Python 3.11+
- Git（Git LFS有効化済み）
- PowerShell 5.1+ (Windows) または bash (Linux/Mac)
- **EDINET API Subscription Key**（無料取得必須）

### EDINET API Key取得

EDINET API v2（2024年4月以降）では Subscription Key が必須です:

1. **申込ページ**: https://disclosure2.edinet-fsa.go.jp/WZEK0020.aspx
2. 「Subscription Key申込」から無料登録
3. メールでキーが即時送付される
4. `.env`ファイルに設定:

```bash
# .env.example をコピー
cp .env.example .env

# エディタで .env を開き、キーを設定
# EDINET_API_KEY=your_subscription_key_here
```

### ローカル環境構築

```powershell
# リポジトリクローン
git clone https://github.com/J1921604/stock-analysis.git
cd stock-analysis

# ワンコマンド起動
.\start.ps1
```

ブラウザで http://localhost:5000 にアクセス

---

## 📚 ドキュメント

| ドキュメント | 説明 | リンク |
|-------------|------|--------|
| **完全実装仕様書** | AI再現用完全仕様 | [docs/完全仕様書.md](https://github.com/J1921604/stock-analysis/blob/main/docs/完全仕様書.md) |
| **要件定義書** | ビジネス要件・受入基準 | [specs/001-stock-analysis-system/checklists/requirements.md](https://github.com/J1921604/stock-analysis/blob/main/specs/001-stock-analysis-system/checklists/requirements.md) |
| **実装計画書** | Phase 1-5実装計画 | [specs/001-stock-analysis-system/plan.md](https://github.com/J1921604/stock-analysis/blob/main/specs/001-stock-analysis-system/plan.md) |
| **デプロイガイド** | GitHub Actions/Pages設定 | [docs/DEPLOY_GUIDE.md](https://github.com/J1921604/stock-analysis/blob/main/docs/DEPLOY_GUIDE.md) |
| **開発憲法** | 品質・セキュリティ原則 | [.specify/memory/constitution.md](https://github.com/J1921604/stock-analysis/blob/main/.specify/memory/constitution.md) |

---

## 🛠️ 技術スタック

### バックエンド

- **Python 3.11+**: データ収集・分析
- **SQLite 3.43+**: 単一ファイルデータベース
- **pandas 2.1.4**: データ正規化
- **lxml 4.9.3**: XBRL解析
- **yfinance 0.2.32**: 株価取得

### フロントエンド

- **sql.js 1.8.0**: ブラウザ内SQLite実行
- **Chart.js 4.4.0**: グラフ描画
- **Tailwind CSS 3.3.0**: ダーク・サイバーパンク風UI

### インフラ

- **GitHub Actions**: 日次自動更新（毎日18:00 JST）
- **GitHub Pages**: 静的サイトホスティング
- **Git LFS**: SQLiteファイル管理

---

## 📂 プロジェクト構造

```
stock-analysis/
├── .github/workflows/       # GitHub Actions設定
├── data/
│   ├── db/                  # SQLiteデータベース
│   └── raw/                 # 生データ（XBRL, 株価）
├── src/                     # フロントエンド（HTML, CSS, JS）
├── scripts/                 # データ収集・分析スクリプト
├── specs/                   # 仕様書・計画書
├── docs/                    # ドキュメント
└── tests/                   # ユニット・E2Eテスト
```

---

## 📊 データソース

| データ種別 | ソース | 更新頻度 |
|-----------|--------|----------|
| 財務諸表 | [EDINET API](https://disclosure2.edinet-fsa.go.jp/) | 四半期ごと |
| 株価 | [Yahoo Finance API](https://finance.yahoo.com/) | 日次 |
| 燃料価格 | 各種市場データ | 日次 |
| JERA業績 | [JERA IRサイト](https://www.jera.co.jp/ir) | 四半期ごと |

---

## 🤝 コントリビューション

このプロジェクトは現在**個人開発モード**です。  
Issue・Pull Requestは受け付けていません。

---

## 📝 ライセンス

MIT License - 詳細は [LICENSE](https://github.com/J1921604/stock-analysis/blob/main/LICENSE) を参照

---

## 🔗 関連リンク

- **デプロイ済みダッシュボード**: https://j1921604.github.io/stock-analysis/
- **GitHub Repository**: https://github.com/J1921604/stock-analysis
- **開発憲法**: [constitution.md v1.0.0](https://github.com/J1921604/stock-analysis/blob/main/.specify/memory/constitution.md)

---

**変更履歴**:
- 2025-11-25: 初版作成（v1.0.0）- 電力3社特化システムとして構築
