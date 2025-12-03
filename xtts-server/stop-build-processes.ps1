#!/usr/bin/env pwsh
<#
.SYNOPSIS
Force stop all build/Python processes
.DESCRIPTION
Safely terminates cl.exe, link.exe, python.exe, pip.exe and related build processes
#>

Write-Host "========================================" -ForegroundColor Green
Write-Host "Parando Processos de Build/Python"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$processes_to_stop = @("cl.exe", "link.exe", "python.exe", "pip.exe", "msbuild.exe", "python3.exe", "vccorlib.exe")

foreach ($proc_name in $processes_to_stop) {
    $procs = Get-Process -Name $proc_name -ErrorAction SilentlyContinue
    if ($procs) {
        foreach ($proc in $procs) {
            try {
                Write-Host "[*] Parando $($proc.ProcessName) (PID: $($proc.Id))..." -ForegroundColor Yellow
                Stop-Process -Id $proc.Id -Force -ErrorAction Stop
                Write-Host "[✓] Parado com sucesso" -ForegroundColor Green
            } catch {
                Write-Host "[!] Falha ao parar: $_" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""
Write-Host "[✓] Cleanup concluído" -ForegroundColor Green
Write-Host ""
Write-Host "Próximas ações:" -ForegroundColor Cyan
Write-Host "  1. Feche o VS Code" -ForegroundColor Gray
Write-Host "  2. Reabra o VS Code" -ForegroundColor Gray
Write-Host "  3. Se persistir, reinicie o Windows" -ForegroundColor Gray
Write-Host ""
