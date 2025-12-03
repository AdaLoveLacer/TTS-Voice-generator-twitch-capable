#!/usr/bin/env pwsh
<#
.SYNOPSIS
Diagnose Windows SDK and Visual Studio installation status
.DESCRIPTION
Checks for Windows SDK headers (io.h), MSVC installation, and PATH/INCLUDE environment setup
#>

Write-Host "========================================" -ForegroundColor Green
Write-Host "Windows SDK / Visual Studio Diagnostics"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 1. Check for io.h in common locations
Write-Host "[*] Procurando io.h em locais comuns..." -ForegroundColor Cyan
$sdk_paths = @(
    "C:\Program Files (x86)\Windows Kits\10\Include",
    "C:\Program Files (x86)\Windows Kits\11\Include",
    "C:\Program Files\Windows Kits\10\Include",
    "C:\Program Files\Windows Kits\11\Include",
    "D:\Program Files (x86)\Windows Kits\10\Include",
    "D:\Program Files (x86)\Windows Kits\11\Include",
    "F:\Windows Kits\10\Include",
    "F:\Windows Kits\11\Include"
)

$io_h_found = $false
foreach ($path in $sdk_paths) {
    if (Test-Path $path) {
        $io_h = Get-ChildItem -Path $path -Filter "io.h" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($io_h) {
            Write-Host "[✓] Encontrado io.h em: $($io_h.FullName)" -ForegroundColor Green
            $io_h_found = $true
        }
    }
}

if (-not $io_h_found) {
    Write-Host "[!] io.h NÃO ENCONTRADO em nenhuma localização comum" -ForegroundColor Red
}

Write-Host ""

# 2. Check Windows Kits installation
Write-Host "[*] Verificando instalação do Windows Kits..." -ForegroundColor Cyan
$kits_found = @()
foreach ($path in $sdk_paths) {
    if (Test-Path $path) {
        $kits_found += $path
    }
}

if ($kits_found.Count -gt 0) {
    Write-Host "[✓] Encontrados diretórios Windows Kits:" -ForegroundColor Green
    foreach ($kit in $kits_found) {
        Write-Host "    - $kit"
    }
} else {
    Write-Host "[!] Nenhum diretório Windows Kits encontrado" -ForegroundColor Red
}

Write-Host ""

# 3. Check MSVC installation
Write-Host "[*] Verificando instalação do MSVC..." -ForegroundColor Cyan
$msvc_paths = @(
    "F:\C++\dev\VC\Tools\MSVC",
    "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC",
    "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC"
)

$msvc_found = $false
foreach ($path in $msvc_paths) {
    if (Test-Path $path) {
        $versions = Get-ChildItem -Path $path -Directory | Sort-Object -Property Name -Descending
        if ($versions) {
            Write-Host "[✓] MSVC encontrado em: $($versions[0].FullName)" -ForegroundColor Green
            $msvc_found = $true
            $latest_msvc = $versions[0].FullName
        }
    }
}

if (-not $msvc_found) {
    Write-Host "[!] MSVC não encontrado" -ForegroundColor Red
}

Write-Host ""

# 4. Check environment variables
Write-Host "[*] Verificando variáveis de ambiente..." -ForegroundColor Cyan
$include_env = $env:INCLUDE
if ($include_env) {
    Write-Host "[✓] INCLUDE está definido:" -ForegroundColor Green
    $include_env.Split(";") | ForEach-Object { if ($_) { Write-Host "    - $_" } }
} else {
    Write-Host "[!] INCLUDE não está definido" -ForegroundColor Red
}

Write-Host ""

# 5. Try to locate vcvars64.bat
Write-Host "[*] Procurando vcvars64.bat..." -ForegroundColor Cyan
$vcvars_paths = @(
    "F:\C++\dev\VC\Auxiliary\Build\vcvars64.bat",
    "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat",
    "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
)

$vcvars_found = $false
foreach ($path in $vcvars_paths) {
    if (Test-Path $path) {
        Write-Host "[✓] vcvars64.bat encontrado em: $path" -ForegroundColor Green
        $vcvars_found = $true
        $vcvars_file = $path
    }
}

if (-not $vcvars_found) {
    Write-Host "[!] vcvars64.bat não encontrado" -ForegroundColor Red
}

Write-Host ""

# 6. Summary and recommendation
Write-Host "========================================" -ForegroundColor Green
Write-Host "RESUMO E RECOMENDAÇÕES"
Write-Host "========================================" -ForegroundColor Green

$issues = @()

if (-not $io_h_found) {
    $issues += "io.h não encontrado (Windows SDK headers ausentes)"
}

if ($kits_found.Count -eq 0) {
    $issues += "Windows Kits não está instalado"
}

if (-not $msvc_found) {
    $issues += "MSVC não encontrado"
}

if (-not $vcvars_found) {
    $issues += "vcvars64.bat não encontrado"
}

if ($issues.Count -eq 0) {
    Write-Host "[✓] Tudo parece estar configurado corretamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximo passo: Tente instalar TTS novamente:" -ForegroundColor Cyan
    Write-Host "  py -3.11 start.py install-tts" -ForegroundColor Yellow
} else {
    Write-Host "[!] Problemas detectados:" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "    - $issue"
    }
    Write-Host ""
    Write-Host "SOLUÇÃO RECOMENDADA:" -ForegroundColor Cyan
    Write-Host "  1. Instale o Windows 11 SDK ou Visual Studio Build Tools" -ForegroundColor Yellow
    Write-Host "     Execute como Administrador:" -ForegroundColor Yellow
    Write-Host "       py -3.11 start.py install-sdk" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  2. Ou baixe manualmente de:" -ForegroundColor Yellow
    Write-Host "     - Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/" -ForegroundColor Yellow
    Write-Host "     - Windows 11 SDK: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" -ForegroundColor Yellow
}

Write-Host ""
