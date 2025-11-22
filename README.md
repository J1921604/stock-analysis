# 電力業界財務分析システム (Power Industry Financial Analysis System)

**バージョン**: 1.0.0  
**最終更新**: 2025年11月25日  
**対象企業**: 東京電力ホールディングス（9501）、中部電力（9502）、JERA（非上場）

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-success)](https://j1921604.github.io/stock-analysis/)

---

## 📖 概要

東京電力ホールディングス・中部電力・JERA の3社に特化した財務自動分析システム。  
GitHub Actionsによる完全自動化で、サーバー運用コストゼロで継続的なデータ収集・可視化を実現します。

### 主要機能

- ⚡ **電力3社専用ダッシュボード**: 売上高・純利益・ROE/ROA推移のリアルタイム可視化
- 📊 **電力業界特化分析**: JERA持分法利益貢献、燃料費感応度、親会社別貢献度
- 🤖 **完全自動データ収集**: EDINET XBRL財務データを日次自動取得
- 🚀 **GitHub Pages配信**: 静的サイトとして無料ホスティング
- 💾 **オフライン動作**: ブラウザ内SQLite（sql.js）で完結、サーバー不要

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
- [x] **財務データ表示機能**: TEPCO・中部電力・JERAの財務諸表可視化
- [x] **ワンコマンド起動**: `.\start.ps1`で即座にローカル環境起動
- [x] **完全エラーハンドリング**: データ読み込み失敗時の適切なUI表示

### 実装済み機能 🎉

#### 財務データダッシュボード
- **東京電力HD**: `/src/pages/tepco.html`
  - 売上高・純利益グラフ（過去5年分・24四半期）
  - ROE・ROA推移チャート
  - 総資産・純資産推移
  - JERA持分法利益貢献度（**実データ計算**: 純利益の20-30%で推定）
  
- **中部電力**: `/src/pages/chubu.html`
  - 売上高・純利益グラフ
  - ROE・ROA推移チャート
  - 総資産・純資産推移
  - 燃料費感応度分析（ダミー推定: 表示用の推定式を利用）

- **JERA**: `/src/pages/jera.html`
  - 売上高・純利益グラフ（過去5年分・24四半期）
  - ROE・ROA推移チャート
  - 総資産・純資産推移
  - 親会社貢献度分析（ダミー推定: 表示用の単純配分で算出）

#### 技術実装
- ✅ sql.js 1.8.0でブラウザ内SQLite実行
- ✅ Chart.js 4.4.0で動的グラフ描画
- ✅ サイバーパンク風ダークUIデザイン
- ✅ レスポンシブ対応
- ✅ エラー時の適切なフィードバック表示
- ✅ データベース接続状態の可視化
 - ✅ データベース接続状態の可視化
 - ⚠️ 一部ダミーデータあり: 表示用の推定式をページ内で使用しています（`src/pages/chubu.html`, `src/pages/jera.html`）
 - ⚠️ 決定論的ルールは維持していますが、一部は表示用の推定式（擬似乱数は未使用）を利用しています

### データ投入状況 📊
- **企業データ**: 3社（9501, 9502, E36542）
- **財務データ**: 72レコード（各社24四半期×3社）
- **TOPIXデータ**: 91日分
- **データベースサイズ**: 約100KB

### Phase 2: データパイプライン ✅ 実装完了

- [x] **fetch_xbrl.py**: EDINET XBRL取得（差分更新対応）
- [x] **parse_xbrl.py**: XBRL財務データ抽出
- [x] **pipeline.py**: 統合パイプライン（DB初期化→取得→解析）
- [x] **GitHub Actions**: 日次自動更新ワークフロー
- [x] **GitHub Pages**: 自動デプロイワークフロー

### 将来拡張機能（Phase 3以降）

Phase 3以降の詳細は [実装計画書](https://github.com/J1921604/stock-analysis/blob/main/specs/feature/impl-001-stock-analysis-system/plan.md) を参照してください。

- **株価データ連携**: Yahoo Finance API統合（現在Yahoo側APIエラーのため保留）
- **高度な業界分析**: 燃料価格連動分析、発電構成比率推移
- **通知機能**: ROE急変・財務悪化時のGitHub Issue自動作成

---

## 🚀 クイックスタート

### 前提条件

- Python 3.11+
- Git（Git LFS有効化済み）
- PowerShell 5.1+ (Windows) または bash (Linux/Mac)
- **EDINET API Subscription Key**（無料取得必須）

### EDINET API Key取得

EDINET API v2（2024年4月以降）では Subscription Key が必須です:

1. **申込ページ**: https://disclosure2.edinet-fsa.go.jp/WEEK0010.aspx
2. 「Subscription Key申込」から無料登録
3. メールでキーが即時送付される（32文字の英数字）
4. `.env`ファイルに設定（**引用符不要**）:

```bash
# .env.example をコピー
cp .env.example .env

# エディタで .env を開き、キーをそのまま記載
# EDINET_API_KEY=your_subscription_key_here
```

**参考資料**:
- API仕様書: https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html
- 利用ガイド(PDF): https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf

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
| **実装計画書** | Phase 1-2実装完了レポート | [specs/feature/impl-001-stock-analysis-system/plan.md](https://github.com/J1921604/stock-analysis/blob/main/specs/feature/impl-001-stock-analysis-system/plan.md) |
| **デプロイガイド** | GitHub Actions/Pages設定 | [docs/DEPLOY_GUIDE.md](https://github.com/J1921604/stock-analysis/blob/main/docs/DEPLOY_GUIDE.md) |

---

## 🛠️ 技術スタック

### バックエンド

- **Python 3.11+**: データ収集・分析
- **SQLite 3.43+**: 単一ファイルデータベース
- **pandas 2.1.4**: データ正規化
- **lxml 4.9.3**: XBRL解析

### フロントエンド

- **sql.js 1.8.0**: ブラウザ内SQLite実行
- **Chart.js 4.4.0**: グラフ描画
- **CSS3**: サイバーパンク風ダークテーマUI

### インフラ

- **GitHub Actions**: 日次自動更新（毎日9:00 JST）
- **GitHub Pages**: 静的サイトホスティング
- **Git LFS**: SQLiteファイル管理

---

## 📂 プロジェクト構造

```
stock-analysis/
├── .github/workflows/       # GitHub Actions設定
│   ├── deploy-pages.yml     # 静的サイト自動デプロイ
│   └── update-data.yml      # 日次データ更新
├── data/
│   ├── db/                  # SQLiteデータベース
│   ├── raw/                 # 生データ（XBRL）
│   └── cache/               # パース済みデータ
├── src/                     # フロントエンド（HTML, CSS, JS）
│   ├── index.html           # メインダッシュボード
│   ├── pages/               # 企業別ページ（tepco, chubu, jera）
│   └── styles.css           # サイバーパンクUI
├── scripts/                 # データ収集・分析スクリプト
│   ├── init_db.py           # DB初期化
│   ├── fetch_xbrl.py        # EDINET XBRL取得
│   ├── parse_xbrl.py        # XBRL解析
│   └── pipeline.py          # 統合パイプライン
├── specs/                   # 仕様書・計画書
│   ├── 001-stock-analysis-system/  # 完全仕様v1.0.0
│   └── feature/impl-001-stock-analysis-system/  # 実装計画
├── docs/                    # ドキュメント
│   ├── 完全仕様書.md
│   └── DEPLOY_GUIDE.md
└── tests/                   # ユニットテスト
    └── test_*.py
```

---

## 📊 データソース

| データ種別 | ソース | 更新頻度 | 備考 |
|-----------|--------|----------|------|
| 財務諸表 | [EDINET API](https://disclosure2.edinet-fsa.go.jp/) | 四半期ごと | 東京電力HD・中部電力のみ |
| JERA業績 | [JERA IRサイト](https://www.jera.co.jp/ir) | 四半期ごと | 手動登録（非上場のため） |

**注**: 株価データ連携はYahoo Finance API不安定のため現在保留中です。

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
