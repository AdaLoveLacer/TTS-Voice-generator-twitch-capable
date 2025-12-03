#!/usr/bin/env pwsh
<#
.SYNOPSIS
Diagnose and kill CPU-consuming processes related to build/Python
.DESCRIPTION
Identifies processes consuming high CPU and helps terminate them safely
#>

Write-Host "========================================" -ForegroundColor Green
Write-Host "Diagnóstico de Processos com Alto CPU"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Get top 10 processes by CPU usage
Write-Host "[*] Top 10 processos por uso de CPU:" -ForegroundColor Cyan
Write-Host ""

$processes = Get-Process | Sort-Object -Property CPU -Descending | Select-Object -First 10 @{Name="PID";Expression={$_.Id}}, @{Name="Nome";Expression={$_.ProcessName}}, @{Name="CPU(s)";Expression={[math]::Round($_.CPU, 2)}}, @{Name="Memória(MB)";Expression={[math]::Round($_.WorkingSet / 1MB, 2)}}

$processes | Format-Table -AutoSize

Write-Host ""

# Look for known problematic processes
Write-Host "[*] Procurando processos problémáticos..." -ForegroundColor Cyan
Write-Host ""

$suspects = @("cl.exe", "link.exe", "python.exe", "pip.exe", "msbuild.exe", "python3.exe")
$found_suspects = @()

foreach ($proc_name in $suspects) {
    $procs = Get-Process -Name $proc_name -ErrorAction SilentlyContinue
    if ($procs) {
        $found_suspects += $procs
        foreach ($proc in $procs) {
            Write-Host "[!] Encontrado: $($proc.ProcessName) (PID: $($proc.Id), CPU: $([math]::Round($proc.CPU, 2))s, RAM: $([math]::Round($proc.WorkingSet / 1MB, 2))MB)" -ForegroundColor Yellow
        }
    }
}

if ($found_suspects.Count -eq 0) {
    Write-Host "[✓] Nenhum processo compilador/Python problemático encontrado" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[*] Processos encontrados que podem estar causando o problema:" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Read-Host "Deseja terminar estes processos? (s/n)"
    if ($response -eq 's' -or $response -eq 'S') {
        foreach ($proc in $found_suspects) {
            try {
                Stop-Process -Id $proc.Id -Force
                Write-Host "[✓] Processo $($proc.ProcessName) (PID: $($proc.Id)) terminado" -ForegroundColor Green
            } catch {
                Write-Host "[!] Falha ao terminar $($proc.ProcessName): $_" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Recomendações"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[i] Se o VS Code está lento/travado:" -ForegroundColor Cyan
Write-Host "    1. Feche o VS Code completamente" -ForegroundColor Gray
Write-Host "    2. Execute: py -3.11 stop-build-processes.ps1" -ForegroundColor Gray
Write-Host "    3. Abra o VS Code novamente" -ForegroundColor Gray
Write-Host ""
Write-Host "[i] Se um processo pip/compilador está travado:" -ForegroundColor Cyan
Write-Host "    1. Execute este script e termine os processos" -ForegroundColor Gray
Write-Host "    2. Execute: py -3.11 start.py 4  (limpar e reinstalar)" -ForegroundColor Gray
Write-Host ""
Write-Host "[i] Se o problema persistir:" -ForegroundColor Cyan
Write-Host "    1. Reinicie o Windows" -ForegroundColor Gray
Write-Host "    2. Abra um novo terminal PowerShell" -ForegroundColor Gray
Write-Host "    3. Execute: py -3.11 start.py install" -ForegroundColor Gray
Write-Host ""
