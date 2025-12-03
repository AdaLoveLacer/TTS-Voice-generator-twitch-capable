# Setup Windows SDK Headers
# Localiza e configura Windows SDK para compilação C++

$ErrorActionPreference = "Stop"

Write-Host "[*] Configurando Windows SDK..." -ForegroundColor Cyan

# Possíveis locais do Windows SDK
$possiblePaths = @(
    "C:\Program Files (x86)\Windows Kits\10",
    "C:\Program Files (x86)\Windows Kits\11",
    "D:\Windows Kits\10",
    "D:\Windows Kits\11",
    "F:\Windows Kits\10",
    "F:\Windows Kits\11"
)

$foundPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\Include") {
        $foundPath = $path
        Write-Host "[✓] Windows SDK encontrado em: $path" -ForegroundColor Green
        break
    }
}

if (-not $foundPath) {
    Write-Host "[!] Windows SDK não encontrado" -ForegroundColor Yellow
    Write-Host "    Tentando via Visual Studio..."
    
    # Tenta encontrar via VS 2022
    $vsPath = "C:\Program Files\Microsoft Visual Studio\2022\BuildTools"
    if (Test-Path $vsPath) {
        $foundPath = $vsPath
        Write-Host "[✓] Visual Studio BuildTools encontrado" -ForegroundColor Green
    }
}

if (-not $foundPath) {
    Write-Host "[X] Não foi possível localizar Windows SDK ou Visual Studio" -ForegroundColor Red
    Write-Host ""
    Write-Host "Opções:"
    Write-Host "  1. Instale 'Visual Studio Build Tools 2022' de https://visualstudio.microsoft.com/"
    Write-Host "  2. Ou Windows 11 SDK de https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/"
    exit 1
}

# Configurar variáveis de ambiente
$includeDir = "$foundPath\Include\10.0.22621.0\ucrt"
if (-not (Test-Path $includeDir)) {
    $includeDir = "$foundPath\Include\10.0.22000.0\ucrt"
}
if (-not (Test-Path $includeDir)) {
    $includeDir = "$foundPath\Include\10.0\ucrt"
}

Write-Host "[*] Include dir: $includeDir"
$env:INCLUDE = "$includeDir;$env:INCLUDE"

# Tenta compilação simples de teste
Write-Host "[*] Testando compilação..."
$testCode = @"
#include <stdio.h>
#include <io.h>

int main() {
    printf("OK\n");
    return 0;
}
"@

$testFile = "test_compile.c"
$testExe = "test_compile.exe"

Set-Content -Path $testFile -Value $testCode
cl.exe /TcTest_compile.c /FeTest_compile.exe 2>&1 | Out-Null

if (Test-Path $testExe) {
    Write-Host "[✓] Compilação teste bem-sucedida!" -ForegroundColor Green
    Remove-Item $testFile -Force -ErrorAction SilentlyContinue
    Remove-Item $testExe -Force -ErrorAction SilentlyContinue
} else {
    Write-Host "[!] Compilação teste falhou" -ForegroundColor Yellow
}

Write-Host "[✓] SDK configurado. Tente novamente: python start.py install" -ForegroundColor Green
