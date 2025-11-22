# GitHub Pagesデプロイ手順書

## 概要
このドキュメントは、株式分析システムをGitHub Pagesに自動・手動でデプロイする手順を説明します。

---

## 自動デプロイ（推奨）

### 前提条件
- GitHubリポジトリ: `https://github.com/J1921604/stock-analysis`
- ブランチ: `main`
- GitHub Actions有効化

### デプロイフロー

#### 1. GitHub Actionsワークフロー
`.github/workflows/deploy.yml`が自動的に以下のトリガーで実行されます:

- **プッシュトリガー**: `main`ブランチへのプッシュ時
- **手動トリガー**: GitHub Actions UIから手動実行
- **スケジュールトリガー**: 毎日9時（JST）自動実行（cron: `0 1 * * *`）

#### 2. ビルドステップ
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - Checkout（Git LFS有効化）
      - Python 3.11セットアップ
      - 依存パッケージインストール（requirements.txt）
      - データベース初期化（scripts/init_db.py）
      - データパイプライン実行（プレースホルダー）
      - GitHub Pagesアップロード（srcディレクトリ）
```

#### 3. デプロイステップ
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - GitHub Pagesデプロイ（deploy-pages@v4）
```

#### 4. デプロイ先URL
- **本番URL**: https://j1921604.github.io/stock-analysis/
- **ステータス**: GitHub Actions > Actionsタブで確認

---

## 手動デプロイ

### 手順1: GitHub Pages設定確認

1. GitHubリポジトリにアクセス:
   ```
   https://github.com/J1921604/stock-analysis
   ```

2. **Settings** > **Pages** に移動

3. **Source**設定を確認:
   - **Source**: GitHub Actions
   - **Branch**: 設定不要（GitHub Actionsが自動管理）

4. **Custom domain**（オプション）:
   - カスタムドメインを使用する場合は入力
   - 例: `stock-analysis.example.com`

### 手順2: GitHub Actions手動実行

1. リポジトリの **Actions** タブに移動:
   ```
   https://github.com/J1921604/stock-analysis/actions
   ```

2. **Deploy to GitHub Pages** ワークフローを選択

3. **Run workflow** ボタンをクリック

4. **Branch**: `main` を選択

5. **Run workflow** をクリックして実行開始

6. ワークフロー実行状況を確認:
   - 緑色チェックマーク: 成功
   - 赤色Xマーク: 失敗（ログを確認）

### 手順3: デプロイ確認

1. ワークフロー完了後、以下のURLにアクセス:
   ```
   https://j1921604.github.io/stock-analysis/
   ```

2. ページが表示されない場合:
   - 5-10分待機（DNS伝播時間）
   - ブラウザキャッシュをクリア（Ctrl+Shift+R）
   - GitHub Actions実行ログを確認

---

## トラブルシューティング

### エラー1: GitHub Pages設定が見つからない

**原因**: リポジトリ設定でPagesが無効化されている

**解決策**:
1. **Settings** > **Pages** に移動
2. **Source**: `GitHub Actions` を選択
3. **Save** をクリック

### エラー2: ワークフロー実行が失敗する

**原因**: `requirements.txt`の依存パッケージインストール失敗

**解決策**:
1. `.github/workflows/deploy.yml`のログを確認
2. `requirements.txt`のパッケージバージョンを確認
3. Python 3.11互換性を確認

### エラー3: デプロイ後にページが表示されない

**原因**: `src/index.html`が見つからない

**解決策**:
1. `src/index.html`が存在するか確認
2. `.github/workflows/deploy.yml`の`path: src`を確認
3. GitHub Actions実行ログで`upload-pages-artifact`ステップを確認

### エラー4: データベースファイルが大きすぎる

**原因**: Git LFS未設定、または100MB超えファイル

**解決策**:
1. `.gitattributes`にGit LFS設定を追加:
   ```gitattributes
   *.db filter=lfs diff=lfs merge=lfs -text
   data/db/*.db filter=lfs diff=lfs merge=lfs -text
   ```
2. Git LFSをインストール:
   ```bash
   git lfs install
   git lfs track "*.db"
   git add .gitattributes
   git commit -m "Add Git LFS tracking for *.db"
   git push origin main
   ```

---

## ローカルプレビュー

デプロイ前に、ローカル環境で動作確認を行います。

### 方法1: start.ps1スクリプト（推奨）

```powershell
# 開発サーバー起動（http://localhost:5000）
.\start.ps1

# または、GitHub Pagesを開く
.\start.ps1 2
```

### 方法2: Python HTTPサーバー

```powershell
cd src
python -m http.server 5000
```

ブラウザで`http://localhost:5000`にアクセスして動作確認

---

## デプロイチェックリスト

デプロイ前に以下を確認してください:

- [ ] `src/index.html`が存在する
- [ ] `src/styles.css`が存在する
- [ ] `src/pages/*.html`が存在する
- [ ] `data/db/stock-analysis.db`が初期化済み
- [ ] `.gitattributes`にGit LFS設定がある
- [ ] `requirements.txt`に全依存パッケージが記載されている
- [ ] `.github/workflows/deploy.yml`が正しく設定されている
- [ ] ローカルプレビューで動作確認済み
- [ ] `main`ブランチにマージ済み

---

## GitHub Pages URL一覧

| 環境 | URL | 用途 |
|------|-----|------|
| 本番環境 | https://j1921604.github.io/stock-analysis/ | 公開ページ |
| リポジトリ | https://github.com/J1921604/stock-analysis | ソースコード |
| GitHub Actions | https://github.com/J1921604/stock-analysis/actions | デプロイ状況確認 |
| GitHub Pages設定 | https://github.com/J1921604/stock-analysis/settings/pages | Pages設定 |

---

## 自動デプロイスケジュール

GitHub Actionsは以下のスケジュールで自動実行されます:

- **日次実行**: 毎日9時（JST） - `cron: '0 1 * * *'`（UTC 1:00 = JST 10:00）
- **プッシュ時**: `main`ブランチへのプッシュ時
- **手動実行**: GitHub Actions UIから任意のタイミング

---

## セキュリティ設定

### GitHub Pagesアクセス制御

デフォルトでは、GitHub Pagesは公開ページです。プライベートリポジトリの場合、以下の設定が可能です:

1. **Settings** > **Pages** > **Visibility**
2. **Public** または **Private** を選択

### 環境変数・シークレット

機密情報（APIキー等）は、GitHub Secretsを使用します:

1. **Settings** > **Secrets and variables** > **Actions**
2. **New repository secret** をクリック
3. 名前と値を入力（例: `EDINET_API_KEY`）
4. `.github/workflows/deploy.yml`で参照:
   ```yaml
   env:
     EDINET_API_KEY: ${{ secrets.EDINET_API_KEY }}
   ```

---

## まとめ

- **自動デプロイ**: `main`ブランチにプッシュすると自動デプロイ
- **手動デプロイ**: GitHub Actions UIから手動実行
- **デプロイ先**: https://j1921604.github.io/stock-analysis/
- **ローカルプレビュー**: `.\start.ps1`で確認
- **トラブルシューティング**: GitHub Actionsログを確認

---

## 関連ドキュメント

- [GitHub Pages公式ドキュメント](https://docs.github.com/ja/pages)
- [GitHub Actions公式ドキュメント](https://docs.github.com/ja/actions)
- [Git LFS公式ドキュメント](https://git-lfs.github.com/)
- [実装レポート](IMPLEMENTATION_REPORT.md)
- [完全仕様書](specs/001-stock-analysis-system/spec.md)
