# Stock Analysis System Launcher
param([string]$mode = "1")

Write-Host "株式分析システム" -ForegroundColor Cyan
Write-Host ""

if ($mode -eq "1" -or $mode -eq "") {
    Write-Host "開発サーバーを起動します..." -ForegroundColor Green
    Set-Location src
    Start-Process "http://localhost:5000"
    py -m http.server 5000
} elseif ($mode -eq "2") {
    Write-Host "GitHub Pagesを開きます..." -ForegroundColor Green
    Start-Process "https://j1921604.github.io/stock-analysis/"
} else {
    Write-Host "使用方法:" -ForegroundColor Yellow
    Write-Host "  .\start.ps1      # 開発サーバー起動"
    Write-Host "  .\start.ps1 2    # GitHub Pages表示"
}
