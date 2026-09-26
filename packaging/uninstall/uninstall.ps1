# SquareRoot: полное удаление (Windows).
# Запуск: powershell -ExecutionPolicy Bypass -File uninstall.ps1 [-Path C:\путь\SquareRoot-windows-x86_64.exe]
param([string]$Path = "")

if (Get-Process -Name "SquareRoot*" -ErrorAction SilentlyContinue) {
    Write-Error "Закройте SquareRoot и запустите скрипт ещё раз."; exit 1
}

function Remove-IfExists($p) {
    if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force; Write-Host "удалено: $p" }
}

if ($Path) { Remove-IfExists $Path }
else {
    $dirs = @((Get-Location).Path, "$env:USERPROFILE\Downloads", "$env:USERPROFILE\Desktop")
    foreach ($d in $dirs) { Remove-IfExists (Join-Path $d "SquareRoot-windows-x86_64.exe") }
}

# Остатки распаковки PyInstaller (только после аварийного завершения).
Get-ChildItem -Path $env:TEMP -Directory -Filter "_MEI*" -ErrorAction SilentlyContinue |
    Where-Object { Test-Path (Join-Path $_.FullName "SQUAREROOT_BUNDLE") } |
    ForEach-Object { Remove-IfExists $_.FullName }

Write-Host "SquareRoot удалён полностью. Реестр и AppData программа не использует."
