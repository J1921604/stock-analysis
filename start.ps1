# 株式分析システム ワンコマンド起動スクリプト
# Stock Analysis System - One Command Launcher
# Version: 1.0.0
# Author: GitHub Copilot
# Date: 2025-11-22

# エラー時に停止
$ErrorActionPreference = "Stop"

# 色付きメッセージ関数
function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

# バナー表示
Clear-Host
Write-Host @"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║           株式分析システム 起動スクリプト                ║
║        Stock Analysis System Launcher v1.0.0           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"@ -ForegroundColor Green

Write-Host ""
Write-ColorMessage "起動日時: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Yellow"
Write-Host ""

# ============================================
# 1. 環境チェック
# ============================================

Write-Header "環境チェック"

# Python バージョンチェック
Write-ColorMessage "► Python バージョン確認中..." "Cyan"
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $version = [version]$matches[1]
        if ($version -ge [version]"3.11") {
            Write-ColorMessage "  ✓ $pythonVersion" "Green"
        } else {
            Write-ColorMessage "  ✗ Python 3.11以上が必要です（現在: $pythonVersion）" "Red"
            exit 1
        }
    }
} catch {
    Write-ColorMessage "  ✗ Python が見つかりません" "Red"
    Write-ColorMessage "  → https://www.python.org/downloads/ からインストールしてください" "Yellow"
    exit 1
}

# Node.js バージョンチェック（オプション）
Write-ColorMessage "► Node.js バージョン確認中..." "Cyan"
try {
    $nodeVersion = node --version 2>&1
    if ($nodeVersion -match "v(\d+\.\d+)") {
        Write-ColorMessage "  ✓ $nodeVersion" "Green"
    }
} catch {
    Write-ColorMessage "  ! Node.js が見つかりません（オプション）" "Yellow"
}

# Git バージョンチェック
Write-ColorMessage "► Git バージョン確認中..." "Cyan"
try {
    $gitVersion = git --version 2>&1
    Write-ColorMessage "  ✓ $gitVersion" "Green"
} catch {
    Write-ColorMessage "  ✗ Git が見つかりません" "Red"
    exit 1
}

# ============================================
# 2. 依存関係チェック
# ============================================

Write-Header "依存関係チェック"

# requirements.txt 存在確認
if (Test-Path "requirements.txt") {
    Write-ColorMessage "► requirements.txt が見つかりました" "Green"
    
    # 仮想環境の確認
    if (-not (Test-Path "venv")) {
        Write-ColorMessage "► 仮想環境を作成中..." "Cyan"
        python -m venv venv
        Write-ColorMessage "  ✓ 仮想環境を作成しました" "Green"
    }
    
    # 仮想環境をアクティベート
    Write-ColorMessage "► 仮想環境をアクティベート中..." "Cyan"
    & .\venv\Scripts\Activate.ps1
    
    # 依存関係インストール
    Write-ColorMessage "► 依存関係をインストール中..." "Cyan"
    pip install -q -r requirements.txt
    Write-ColorMessage "  ✓ 依存関係をインストールしました" "Green"
} else {
    Write-ColorMessage "  ! requirements.txt が見つかりません" "Yellow"
}

# ============================================
# 3. データベース確認
# ============================================

Write-Header "データベース確認"

$dbPath = "data\db\stock-analysis.db"

if (Test-Path $dbPath) {
    $dbSize = (Get-Item $dbPath).Length / 1MB
    Write-ColorMessage "  ✓ データベースが見つかりました（サイズ: $([math]::Round($dbSize, 2)) MB）" "Green"
} else {
    Write-ColorMessage "  ! データベースが見つかりません" "Yellow"
    Write-ColorMessage "  → 初回実行時はデータベースを作成します" "Cyan"
    
    # ディレクトリ作成
    if (-not (Test-Path "data\db")) {
        New-Item -ItemType Directory -Path "data\db" -Force | Out-Null
    }
}

# ============================================
# 4. 起動オプション選択
# ============================================

Write-Header "起動オプション"

Write-Host "起動モードを選択してください:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [1] 開発サーバー起動（推奨）" -ForegroundColor White
Write-Host "  [2] データ更新バッチ実行" -ForegroundColor White
Write-Host "  [3] 解析ページをブラウザで開く" -ForegroundColor White
Write-Host "  [4] 全て実行（更新→サーバー起動）" -ForegroundColor White
Write-Host "  [0] 終了" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "選択してください (1-4, 0)"

switch ($choice) {
    "1" {
        # ============================================
        # 開発サーバー起動
        # ============================================
        
        Write-Header "開発サーバー起動"
        
        # GitHub Pages ローカルプレビュー
        if (Test-Path "src\index.html") {
            Write-ColorMessage "► ローカルサーバーを起動中..." "Cyan"
            
            # ポート設定
            $port = 5000
            
            # Python 簡易HTTPサーバー起動
            Write-ColorMessage "  → http://localhost:$port で起動します" "Yellow"
            Write-Host ""
            Write-ColorMessage "  Ctrl+C で終了します" "Gray"
            Write-Host ""
            
            # ブラウザを開く
            Start-Sleep -Seconds 1
            Start-Process "http://localhost:$port"
            
            # サーバー起動
            Push-Location src
            python -m http.server $port
            Pop-Location
            
        } else {
            Write-ColorMessage "  ✗ src\index.html が見つかりません" "Red"
        }
    }
    
    "2" {
        # ============================================
        # データ更新バッチ実行
        # ============================================
        
        Write-Header "データ更新バッチ実行"
        
        # スクリプト存在確認
        if (Test-Path "scripts") {
            Write-ColorMessage "► データ更新を開始します..." "Cyan"
            Write-Host ""
            
            # 株価データ取得
            if (Test-Path "scripts\fetch_prices.py") {
                Write-ColorMessage "  → 株価データ取得中..." "Yellow"
                python scripts\fetch_prices.py --since-db $dbPath
            }
            
            # XBRL取得
            if (Test-Path "scripts\fetch_xbrl.py") {
                Write-ColorMessage "  → XBRLデータ取得中..." "Yellow"
                python scripts\fetch_xbrl.py --since-db $dbPath --rate-limit 1
            }
            
            # パース
            if (Test-Path "scripts\parse_xbrl.py") {
                Write-ColorMessage "  → データ解析中..." "Yellow"
                python scripts\parse_xbrl.py --input data\raw\xbrl --output data\normalized
            }
            
            # DB更新
            if (Test-Path "scripts\import_to_db.py") {
                Write-ColorMessage "  → データベース更新中..." "Yellow"
                python scripts\import_to_db.py --db $dbPath --input data\normalized
            }
            
            # 解析実行
            if (Test-Path "scripts\analyze.py") {
                Write-ColorMessage "  → 解析実行中..." "Yellow"
                python scripts\analyze.py --db $dbPath --output analysis-results.json
            }
            
            Write-Host ""
            Write-ColorMessage "✓ データ更新が完了しました" "Green"
            
        } else {
            Write-ColorMessage "  ✗ scripts フォルダが見つかりません" "Red"
        }
        
        Write-Host ""
        Write-Host "Enterキーを押して終了..."
        Read-Host
    }
    
    "3" {
        # ============================================
        # 解析ページをブラウザで開く
        # ============================================
        
        Write-Header "解析ページ表示"
        
        # GitHub Pages URL（本番環境）
        $pagesUrl = "https://j1921604.github.io/stock-analysis/"
        
        Write-ColorMessage "► ブラウザで解析ページを開きます..." "Cyan"
        Write-ColorMessage "  → $pagesUrl" "Yellow"
        Write-Host ""
        
        Start-Process $pagesUrl
        
        Write-ColorMessage "✓ ブラウザでページを開きました" "Green"
        Write-Host ""
        
        # 自動終了
        Start-Sleep -Seconds 2
    }
    
    "4" {
        # ============================================
        # 全て実行
        # ============================================
        
        Write-Header "フル実行モード"
        
        # データ更新
        Write-ColorMessage "► STEP 1: データ更新" "Cyan"
        if (Test-Path "scripts") {
            # 株価データ取得
            if (Test-Path "scripts\fetch_prices.py") {
                Write-ColorMessage "  → 株価データ取得中..." "Yellow"
                python scripts\fetch_prices.py --since-db $dbPath
            }
            
            # XBRL取得
            if (Test-Path "scripts\fetch_xbrl.py") {
                Write-ColorMessage "  → XBRLデータ取得中..." "Yellow"
                python scripts\fetch_xbrl.py --since-db $dbPath --rate-limit 1
            }
            
            # パース
            if (Test-Path "scripts\parse_xbrl.py") {
                Write-ColorMessage "  → データ解析中..." "Yellow"
                python scripts\parse_xbrl.py --input data\raw\xbrl --output data\normalized
            }
            
            # DB更新
            if (Test-Path "scripts\import_to_db.py") {
                Write-ColorMessage "  → データベース更新中..." "Yellow"
                python scripts\import_to_db.py --db $dbPath --input data\normalized
            }
            
            # 解析実行
            if (Test-Path "scripts\analyze.py") {
                Write-ColorMessage "  → 解析実行中..." "Yellow"
                python scripts\analyze.py --db $dbPath --output analysis-results.json
            }
            
            Write-ColorMessage "  ✓ データ更新完了" "Green"
        }
        
        Write-Host ""
        
        # サーバー起動
        Write-ColorMessage "► STEP 2: サーバー起動" "Cyan"
        if (Test-Path "src\index.html") {
            $port = 5000
            Write-ColorMessage "  → http://localhost:$port で起動します" "Yellow"
            Write-Host ""
            
            # ブラウザを開く
            Start-Sleep -Seconds 1
            Start-Process "http://localhost:$port"
            
            Write-ColorMessage "  Ctrl+C で終了します" "Gray"
            Write-Host ""
            
            # サーバー起動
            Push-Location src
            python -m http.server $port
            Pop-Location
        }
    }
    
    "0" {
        Write-ColorMessage "終了します..." "Yellow"
        exit 0
    }
    
    default {
        Write-ColorMessage "無効な選択です" "Red"
        exit 1
    }
}

# PowerShellを閉じる（サーバー起動モード以外）
if ($choice -ne "1" -and $choice -ne "4") {
    exit 0
}
