# 設定錯誤處理
$ErrorActionPreference = "Stop"

# 設定日誌
$logFile = ".\logs\scraper_$(Get-Date -Format 'yyyyMMdd').log"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 確保日誌目錄存在
if (-not (Test-Path ".\logs")) {
    New-Item -ItemType Directory -Path ".\logs"
}

function Write-Log {
    param([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $message" | Out-File -Append -FilePath $logFile
    Write-Host "$timestamp - $message"
}

try {
    Write-Log "開始執行爬蟲程式"
    
    # 切換到程式目錄
    Set-Location $scriptPath
    
    # 啟動虛擬環境並執行 Python 腳本
    & "$scriptPath\venv\Scripts\activate.ps1"
    & python main.py
    
    Write-Log "爬蟲程式執行完成"
}
catch {
    Write-Log "執行過程中發生錯誤: $_"
    exit 1
}
