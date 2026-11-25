# Bật toàn bộ hệ thống trên Windows:  powershell -ExecutionPolicy Bypass -File start.ps1
# Dừng:                               powershell -ExecutionPolicy Bypass -File start.ps1 -Stop
param([switch]$Stop)
Set-Location $PSScriptRoot
$producer = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*stream_producer*main.py*' }
if ($Stop) {
    $producer | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    docker compose stop
    "Đã dừng."
    return
}
docker compose up -d
if (-not $producer) {
    Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "services\stream_producer\main.py" `
        -WindowStyle Hidden -RedirectStandardOutput "data\producer.log" -RedirectStandardError "data\producer.err.log"
}
"Đã bật. Dashboard: http://localhost:8501"
