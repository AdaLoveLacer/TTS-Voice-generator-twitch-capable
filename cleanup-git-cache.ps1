#!/usr/bin/env pwsh
<#
.SYNOPSIS
Clean up git repository by removing cached files that should be ignored
.DESCRIPTION
Safely removes venv, cache, logs and other files from git tracking
#>

Write-Host "========================================" -ForegroundColor Green
Write-Host "Git Cleanup - Remover Arquivos em Cache"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "[X] Erro: Não estamos em um repositório git" -ForegroundColor Red
    exit 1
}

Write-Host "[*] Preparando para remover arquivos de cache do git..." -ForegroundColor Cyan
Write-Host ""

# Array of patterns to remove from git cache
$patterns = @(
    ".vscode/",
    "xtts-server/venv/",
    "venv/",
    ".env",
    ".env.local",
    ".env.*.local",
    "req-no-tts-*.txt",
    "vs_BuildTools.exe",
    "xtts-server/voices/custom/*",
    "xtts-server/voices/embeddings/*",
    "*.log",
    "build/",
    "dist/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".coverage",
    ".coverage.*",
    "*.pyc",
    ".pip-cache/",
    "Releases/",
    "*.whl"
)

# Show what will be removed (dry-run)
Write-Host "[*] Arquivos que serão removidos do git (modo seco):" -ForegroundColor Yellow
Write-Host ""

$total_count = 0
foreach ($pattern in $patterns) {
    $items = Get-Item -Path $pattern -ErrorAction SilentlyContinue -Force
    if ($items) {
        if ($items -is [array]) {
            $count = $items.Count
        } else {
            $count = 1
        }
        Write-Host "    [→] $pattern ($count item(s))" -ForegroundColor Gray
        $total_count += $count
    }
}

Write-Host ""
Write-Host "Total: $total_count arquivos/pastas serão removidos" -ForegroundColor Yellow
Write-Host ""

# Ask for confirmation
$response = Read-Host "Tem certeza que deseja remover estes arquivos do git? (s/n)"
if ($response -ne 's' -and $response -ne 'S') {
    Write-Host "[i] Operação cancelada pelo usuário" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "[*] Removendo arquivos do git..." -ForegroundColor Cyan
Write-Host ""

$removed_count = 0
foreach ($pattern in $patterns) {
    try {
        $items = Get-Item -Path $pattern -ErrorAction SilentlyContinue -Force -Recurse
        if ($items) {
            if ($items -is [array]) {
                foreach ($item in $items) {
                    git rm --cached -r -f $item.FullName 2>$null
                    Write-Host "[✓] Removido: $($item.FullName)" -ForegroundColor Green
                    $removed_count++
                }
            } else {
                git rm --cached -r -f $items.FullName 2>$null
                Write-Host "[✓] Removido: $($items.FullName)" -ForegroundColor Green
                $removed_count++
            }
        }
    } catch {
        Write-Host "[!] Erro ao remover $pattern : $_" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Resumo da Limpeza"
Write-Host "========================================" -ForegroundColor Green
Write-Host "[✓] $removed_count items removidos do git cache" -ForegroundColor Green
Write-Host ""

# Show git status
Write-Host "[*] Status do git:" -ForegroundColor Cyan
Write-Host ""
git status --short | Select-Object -First 20
Write-Host ""

# Suggest commit
Write-Host "[i] Próximas ações:" -ForegroundColor Cyan
Write-Host "    1. Revisar: git status" -ForegroundColor Gray
Write-Host "    2. Commit:  git commit -m 'Remove cached venv, logs and sensitive files'" -ForegroundColor Gray
Write-Host "    3. Push:    git push" -ForegroundColor Gray
Write-Host ""

$commit_response = Read-Host "Deseja fazer o commit agora? (s/n)"
if ($commit_response -eq 's' -or $commit_response -eq 'S') {
    Write-Host "[*] Fazendo commit..." -ForegroundColor Cyan
    git add .gitignore
    git commit -m "Remove cached venv, logs, build artifacts and sensitive files

- Remove .vscode/ configuration
- Remove venv/ virtual environment
- Remove .env* files
- Remove temporary requirements files
- Remove build/dist artifacts
- Remove cache and temporary files
- Add comprehensive .gitignore"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[✓] Commit realizado com sucesso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Próximo passo: git push" -ForegroundColor Cyan
    } else {
        Write-Host "[!] Erro ao fazer commit" -ForegroundColor Red
    }
}

Write-Host ""
