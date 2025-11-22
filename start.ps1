# 電力業界財務分析システム - ワンコマンド起動スクリプト
# ファイル名: start.ps1
# バージョン: 1.0.0
# 作成日: 2025-11-25
# 用途: ローカル開発環境の起動を1コマンドで実行
# 実行方法: .\start.ps1

# エラー時に停止
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  電力業界財務分析システム v1.0.0" -ForegroundColor Cyan
Write-Host "  ローカルプレビュー起動中..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 仮想環境の確認と有効化
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "[1/4] 仮想環境を有効化しています..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[1/4] 仮想環境が見つかりません。新規作成中..." -ForegroundColor Yellow
    python -m venv venv
    if (Test-Path ".\venv\Scripts\Activate.ps1") {
        & .\venv\Scripts\Activate.ps1
    } else {
        Write-Host "警告: 仮想環境の作成に失敗しました。グローバルPythonを使用します。" -ForegroundColor Red
    }
}

# 2. 依存関係のインストール
Write-Host "[2/4] Python依存関係をインストール中..." -ForegroundColor Yellow
pip install -q -r requirements.txt

# 3. データベースの初期化確認
if (-not (Test-Path ".\data\db\stock-analysis.db")) {
    Write-Host "[3/4] データベースが見つかりません。初期化中..." -ForegroundColor Yellow
    python scripts/init_db.py
} else {
    Write-Host "[3/4] データベース確認OK（TEPCO/中部電力/JERA 3社）" -ForegroundColor Green
}

# 4. ローカルサーバー起動とブラウザ自動起動
Write-Host "[4/4] ローカルサーバーを起動しています..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  起動完了！" -ForegroundColor Green
Write-Host "  URL: http://localhost:5000/index.html" -ForegroundColor Green
Write-Host "  対象企業: 東京電力HD・中部電力・JERA" -ForegroundColor Green
Write-Host "  終了するには Ctrl+C を押してください" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# HTTPサーバー起動（バックグラウンドでジョブとして実行）
Write-Host "サーバーを起動中..." -ForegroundColor Yellow
$srcPath = Join-Path $PSScriptRoot "src"
$serverJob = Start-Job -ScriptBlock { 
    param($path)
    Set-Location $path
    python -m http.server 5000 
} -ArgumentList $srcPath

# サーバー起動待機（3秒）
Start-Sleep -Seconds 3

# ブラウザを自動起動
Write-Host "ブラウザを起動しています..." -ForegroundColor Yellow
Start-Process "http://localhost:5000/index.html"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  サーバーが正常に起動しました！" -ForegroundColor Cyan
Write-Host "  終了するには Ctrl+C を押してください" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ジョブの出力を監視（フォアグラウンドで待機）
try {
    while ($true) {
        Receive-Job -Job $serverJob -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
} finally {
    # Ctrl+C時にジョブを停止
    Stop-Job -Job $serverJob -ErrorAction SilentlyContinue
    Remove-Job -Job $serverJob -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "サーバーを停止しました。" -ForegroundColor Yellow
}
