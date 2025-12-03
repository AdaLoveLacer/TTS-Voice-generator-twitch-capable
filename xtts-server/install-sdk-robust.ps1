#!/usr/bin/env pwsh
<#
.SYNOPSIS
Install Windows SDK or Visual Studio Build Tools
.DESCRIPTION
Attempts to install Windows SDK or Visual Studio Build Tools via:
1. Windows Package Manager (winget)
2. Chocolatey
3. Direct download of vs_BuildTools.exe
#>

$ErrorActionPreference = "Continue"

function Test-AdminPrivilege {
    $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object System.Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Request-AdminElevation {
    Write-Host "[!] Esta operação requer privilégios de Administrador" -ForegroundColor Yellow
    Write-Host ""
    
    $response = Read-Host "Tentar reexecutar como Administrador? (s/n)"
    if ($response -ne 's' -and $response -ne 'S') {
        return $false
    }
    
    $script_path = $MyInvocation.PSCommandPath
    Write-Host "[*] Elevando e reexecutando script..." -ForegroundColor Cyan
    
    try {
        Start-Process -FilePath "pwsh.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$script_path`"" -Verb RunAs -Wait
        return $true
    } catch {
        Write-Host "[X] Falha ao elevar: $_" -ForegroundColor Red
        return $false
    }
}

function Try-Winget {
    Write-Host "[*] Tentando instalar via winget..." -ForegroundColor Cyan
    
    # Check if winget is available
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Host "[!] winget não está disponível" -ForegroundColor Yellow
        return $false
    }
    
    try {
        Write-Host "    Instalando Windows SDK 11..." -ForegroundColor Gray
        & winget install --id Microsoft.WindowsSDK --version=11.0 --silent --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] Windows SDK instalado com sucesso via winget" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "[!] Erro com winget: $_" -ForegroundColor Yellow
    }
    
    return $false
}

function Try-Chocolatey {
    Write-Host "[*] Tentando instalar via Chocolatey..." -ForegroundColor Cyan
    
    # Check if choco is available
    $choco = Get-Command choco -ErrorAction SilentlyContinue
    if (-not $choco) {
        Write-Host "[!] Chocolatey não está disponível" -ForegroundColor Yellow
        return $false
    }
    
    try {
        Write-Host "    Instalando Windows SDK..." -ForegroundColor Gray
        & choco install windows-sdk-10.1 -y --confirm --no-progress
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[✓] Windows SDK instalado com sucesso via Chocolatey" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "[!] Erro com Chocolatey: $_" -ForegroundColor Yellow
    }
    
    return $false
}

function Try-VSBuildTools {
    Write-Host "[*] Tentando baixar Visual Studio Build Tools..." -ForegroundColor Cyan
    
    # Check admin
    if (-not (Test-AdminPrivilege)) {
        Write-Host "[!] É necessário privilégios de Administrador para instalar Build Tools" -ForegroundColor Red
        return (Request-AdminElevation)
    }
    
    $vs_url = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
    $tmp_dir = [System.IO.Path]::GetTempPath()
    $installer_path = Join-Path $tmp_dir "vs_BuildTools.exe"
    
    try {
        # Download
        Write-Host "    Baixando vs_BuildTools.exe (~1.5 MB)..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $vs_url -OutFile $installer_path -UseBasicParsing -ErrorAction Stop
        
        if (-not (Test-Path $installer_path)) {
            Write-Host "[!] Falha ao baixar instalador" -ForegroundColor Red
            return $false
        }
        
        Write-Host "    Executando instalador (isso pode levar 5-15 minutos)..." -ForegroundColor Gray
        Write-Host "    Instalando C++ Build Tools + Windows SDK..." -ForegroundColor Gray
        
        # Run installer with C++ workload and Windows SDK
        & $installer_path `
            --add Microsoft.VisualStudio.Workload.VCTools `
            --add Microsoft.VisualStudio.Component.Windows10SDK.22000 `
            --includeRecommended `
            --quiet `
            --wait `
            --norestart
        
        if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 3010) {
            Write-Host "[✓] Visual Studio Build Tools + SDK instalados com sucesso" -ForegroundColor Green
            
            # Clean up
            Remove-Item $installer_path -ErrorAction SilentlyContinue
            return $true
        } else {
            Write-Host "[!] Instalador retornou erro: $LASTEXITCODE" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "[X] Erro durante instalação: $_" -ForegroundColor Red
        return $false
    }
}

# Main
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Instalador do Windows SDK/Build Tools"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Try all methods
if (Try-Winget) {
    exit 0
}

if (Try-Chocolatey) {
    exit 0
}

if (Try-VSBuildTools) {
    exit 0
}

# If all fail, show manual instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "Todas as opções automáticas falharam"
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "Instale manualmente seguindo um destes passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opção 1: Visual Studio Build Tools 2022 (recomendado)" -ForegroundColor Cyan
Write-Host "  1. Abra: https://visualstudio.microsoft.com/downloads/" -ForegroundColor Gray
Write-Host "  2. Procure por 'Build Tools for Visual Studio 2022'" -ForegroundColor Gray
Write-Host "  3. Clique 'Download'" -ForegroundColor Gray
Write-Host "  4. Execute o instalador" -ForegroundColor Gray
Write-Host "  5. Selecione 'C++ build tools'" -ForegroundColor Gray
Write-Host "  6. Clique 'Install'" -ForegroundColor Gray
Write-Host ""
Write-Host "Opção 2: Windows 11 SDK" -ForegroundColor Cyan
Write-Host "  1. Abra: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" -ForegroundColor Gray
Write-Host "  2. Clique 'Download'" -ForegroundColor Gray
Write-Host "  3. Execute o instalador e selecione 'SDK Tools'" -ForegroundColor Gray
Write-Host ""
Write-Host "Depois, execute novamente:" -ForegroundColor Yellow
Write-Host "  py -3.11 start.py install-tts" -ForegroundColor Gray
Write-Host ""

exit 1
