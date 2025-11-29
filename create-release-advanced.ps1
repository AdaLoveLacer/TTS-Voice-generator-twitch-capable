# ============================================================================
# SPEAKERBOT RELEASE CREATOR - ADVANCED (PowerShell)
# Cria e compacta um release do projeto
# Oferece opções: ZIP ou 7z
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Option = $null
)

# Cores para output
$colors = @{
    Info    = 'Cyan'
    Success = 'Green'
    Warn    = 'Yellow'
    Error   = 'Red'
    Process = 'Magenta'
}

function Write-Status {
    param($Message, $Type = 'Info')
    $color = $colors[$Type]
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $color
}

function Show-Menu {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "       SPEAKERBOT RELEASE CREATOR - MENU" -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "`nEscolha uma opção:`n"
    Write-Host "  1 - Criar release simples (pasta)" -ForegroundColor White
    Write-Host "  2 - Criar e compactar em ZIP" -ForegroundColor White
    Write-Host "  3 - Criar e compactar em 7z" -ForegroundColor White
    Write-Host "  4 - Criar ambos (ZIP + 7z)" -ForegroundColor White
    Write-Host "  5 - Sair`n" -ForegroundColor White
}

function Get-MenuChoice {
    while ($true) {
        $choice = Read-Host "Digite sua opção (1-5)"
        if ($choice -match '^[1-5]$') {
            return $choice
        }
        Write-Status "Opção inválida! Tente novamente." Error
    }
}

function Create-Release {
    param([string]$ReleaseDir)
    
    Write-Status "Criando estrutura de release..." Process
    
    # Remover release anterior se existir
    if (Test-Path $ReleaseDir) {
        Write-Status "Removendo diretório anterior..." Warn
        Remove-Item -Path $ReleaseDir -Recurse -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
    }
    
    # Criar diretório principal
    New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
    Write-Status "Criado: $ReleaseDir" Success
    
    # Criar estrutura de vozes
    $voiceSubDirs = @('custom', 'embeddings', 'presets')
    foreach ($subdir in $voiceSubDirs) {
        $voicePath = Join-Path $ReleaseDir "xtts-server\voices\$subdir"
        New-Item -ItemType Directory -Path $voicePath -Force | Out-Null
    }
    Write-Status "Estrutura de vozes criada" Success
    
    # Arquivos a copiar da raiz
    $rootFiles = @(
        'ENTREGA-COMPLETA.md',
        'README.md',
        'neural_tts_gpu.py',
        'patch_rvc.py'
    )
    
    foreach ($file in $rootFiles) {
        $sourcePath = Join-Path (Get-Location) $file
        if (Test-Path $sourcePath) {
            Copy-Item -Path $sourcePath -Destination $ReleaseDir -Force -ErrorAction SilentlyContinue
            Write-Status "Copiado: $file" Success
        }
    }
    
    # Arquivos a copiar da pasta xtts-server
    $serverFiles = @(
        'main.py',
        'web_ui.html',
        'manifest.json',
        'service-worker.js',
        'speaker_embedding_manager.py',
        'voice_manager.py',
        'requirements.txt',
        'requirements-cu118.txt',
        'start-server.bat',
        'start-server-auto.bat',
        'install-cuda.bat',
        'pyrightconfig.json',
        'check_torch.py',
        'create_default_voices.py'
    )
    
    $serverDir = Join-Path (Get-Location) 'xtts-server'
    foreach ($file in $serverFiles) {
        $sourcePath = Join-Path $serverDir $file
        if (Test-Path $sourcePath) {
            $destPath = Join-Path $ReleaseDir "xtts-server\$file"
            Copy-Item -Path $sourcePath -Destination $destPath -Force -ErrorAction SilentlyContinue
            Write-Status "Copiado: xtts-server/$file" Success
        }
    }
    
    # Copiar vozes customizadas
    Write-Status "Copiando vozes customizadas..." Process
    $voicesSourcePath = Join-Path $serverDir 'voices\custom'
    $voicesDestPath = Join-Path $ReleaseDir 'xtts-server\voices\custom'
    
    if (Test-Path $voicesSourcePath) {
        # Garantir que o diretório de destino existe
        if (-not (Test-Path $voicesDestPath)) {
            New-Item -ItemType Directory -Path $voicesDestPath -Force | Out-Null
        }
        
        $customVoices = @(Get-ChildItem -Path $voicesSourcePath -Filter "*.wav" -ErrorAction SilentlyContinue)
        if ($customVoices.Count -gt 0) {
            foreach ($voice in $customVoices) {
                $destFile = Join-Path $voicesDestPath $voice.Name
                Copy-Item -Path $voice.FullName -Destination $destFile -Force
                if (Test-Path $destFile) {
                    Write-Status "Voz copiada: $($voice.Name)" Success
                } else {
                    Write-Status "Erro ao copiar voz: $($voice.Name)" Error
                }
            }
        } else {
            Write-Status "Nenhuma voz customizada encontrada" Warn
        }
    } else {
        Write-Status "Pasta de vozes não encontrada: $voicesSourcePath" Warn
    }
    
    # Copiar embeddings pré-calculados
    Write-Status "Copiando embeddings pré-calculados..." Process
    $embeddingsSourcePath = Join-Path $serverDir 'voices\embeddings'
    $embeddingsDestPath = Join-Path $ReleaseDir 'xtts-server\voices\embeddings'
    
    if (Test-Path $embeddingsSourcePath) {
        # Garantir que o diretório de destino existe
        if (-not (Test-Path $embeddingsDestPath)) {
            New-Item -ItemType Directory -Path $embeddingsDestPath -Force | Out-Null
        }
        
        $embeddings = @(Get-ChildItem -Path $embeddingsSourcePath -Filter "*.npy" -ErrorAction SilentlyContinue)
        if ($embeddings.Count -gt 0) {
            foreach ($emb in $embeddings) {
                $destFile = Join-Path $embeddingsDestPath $emb.Name
                Copy-Item -Path $emb.FullName -Destination $destFile -Force
                if (Test-Path $destFile) {
                    Write-Status "Embedding copiado: $($emb.Name)" Success
                } else {
                    Write-Status "Erro ao copiar embedding: $($emb.Name)" Error
                }
            }
        } else {
            Write-Status "Nenhum embedding encontrado" Warn
        }
    } else {
        Write-Status "Pasta de embeddings não encontrada: $embeddingsSourcePath" Warn
    }
    
    # Copiar presets customizados
    Write-Status "Copiando presets customizados..." Process
    $presetsSourcePath = Join-Path $serverDir 'voices\presets'
    $presetsDestPath = Join-Path $ReleaseDir 'xtts-server\voices\presets'
    
    if (Test-Path $presetsSourcePath) {
        # Garantir que o diretório de destino existe
        if (-not (Test-Path $presetsDestPath)) {
            New-Item -ItemType Directory -Path $presetsDestPath -Force | Out-Null
        }
        
        $presets = @(Get-ChildItem -Path $presetsSourcePath -Filter "*.json" -ErrorAction SilentlyContinue)
        if ($presets.Count -gt 0) {
            foreach ($preset in $presets) {
                $destFile = Join-Path $presetsDestPath $preset.Name
                Copy-Item -Path $preset.FullName -Destination $destFile -Force
                if (Test-Path $destFile) {
                    Write-Status "Preset copiado: $($preset.Name)" Success
                } else {
                    Write-Status "Erro ao copiar preset: $($preset.Name)" Error
                }
            }
        } else {
            Write-Status "Nenhum preset encontrado" Warn
        }
    } else {
        Write-Status "Pasta de presets não encontrada: $presetsSourcePath" Warn
    }
    
    # Gerar README
    Create-ReleaseReadme $ReleaseDir
}

function Create-ReleaseReadme {
    param([string]$ReleaseDir)
    
    $readmeContent = @"
# 📦 SPEAKERBOT RELEASE

Data de Criação: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')

## 📋 Conteúdo

Este é um release completo do Speakerbot com todos os arquivos necessários para executar.

### Arquivos Incluídos

**Raiz do Projeto:**
- \`neural_tts_gpu.py\` - Processador de TTS com otimizações GPU
- \`patch_rvc.py\` - Patch para compatibilidade com RVC
- \`ENTREGA-COMPLETA.md\` - Documentação completa do projeto

**Pasta xtts-server:**
- \`main.py\` - Servidor FastAPI com todos os endpoints
- \`web_ui.html\` - Interface web com todas as funcionalidades
- \`manifest.json\` - Manifest PWA para instalação como app
- \`service-worker.js\` - Service Worker para cache offline
- \`speaker_embedding_manager.py\` - Gerenciador de embeddings de vozes
- \`voice_manager.py\` - Gerenciador de vozes customizadas
- \`requirements.txt\` - Dependências Python
- \`requirements-cu118.txt\` - Dependências com CUDA 11.8
- \`start-server.bat\` - Script para iniciar servidor
- \`start-server-auto.bat\` - Script automático com GUI
- \`install-cuda.bat\` - Instalador de suporte CUDA
- \`pyrightconfig.json\` - Configuração do Pylance
- \`check_torch.py\` - Verificador de configuração PyTorch
- \`create_default_voices.py\` - Criador de vozes padrão
- Pasta \`voices/\` - Estrutura para vozes personalizadas:
  - \`custom/\` - Vozes customizadas pelo usuário
  - \`embeddings/\` - Cache de embeddings pré-calculados
  - \`presets/\` - Presets personalizados de síntese

## 🚀 Como Usar

### 1. Instalar Dependências

\`\`\`bash
cd xtts-server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

**Com CUDA (GPU acelerada):**

\`\`\`bash
venv\Scripts\activate
install-cuda.bat
pip install -r requirements-cu118.txt
\`\`\`

### 2. Iniciar Servidor

**Opção 1: Manual**
\`\`\`bash
cd xtts-server
python main.py
\`\`\`

**Opção 2: Script automático (recomendado)**
\`\`\`bash
start-server-auto.bat
\`\`\`

### 3. Acessar Interface Web

A interface abre automaticamente ao iniciar o servidor em:
\`\`\`
http://localhost:8877
\`\`\`

Ou acesse manualmente no navegador após iniciar:
- Local: http://127.0.0.1:8877
- Rede: http://<seu-ip>:8877 (de outro computador)

### 4. Instalar como Aplicativo (PWA)

**Chrome/Edge:**
1. Abra http://localhost:8877
2. Clique no ícone de instalação (canto superior direito)
3. Selecione "Instalar Speakerbot"

**Firefox:**
1. Abra http://localhost:8877
2. Menu → Instalar aplicativo web

**iOS (Safari):**
1. Abra http://localhost:8877
2. Compartilhar → Adicionar à Tela de Início

**Android (Chrome):**
1. Abra http://localhost:8877
2. Menu → Instalar app

## ⚙️ Melhorias Implementadas

### 🌐 Progressive Web App (PWA)
✅ Instalável: Instale como aplicativo nativo no desktop/mobile
✅ Offline Support: Funciona offline com service worker e cache
✅ Sync Background: Sincronização em background quando volta online
✅ Push Notifications: Notificações de conclusão de síntese
✅ Manifesto PWA: Com ícones, shortcuts e configurações de app

### Audio Quality
✅ Sample Rate: 24000Hz (padrão XTTS v2)
✅ GPT Cond Length: Controle de 3-30 segundos
✅ Múltiplas Referências: Suporte 1-5 arquivos WAV (150MB total)
✅ Sanitização: Validação e limpeza de áudio para estabilidade GPU

### User Experience
✅ Persistência: Configurações salvas automaticamente
✅ Presets Customizados: Salve e carregue suas configurações favoritas
✅ 7 Presets Pré-configurados: Natural, Lento, Rápido, Robótico, Expressivo, Sussurro, Dramático
✅ Tema Dark: Interface visual moderno com efeitos neon
✅ Abertura Automática: Navegador abre em http://localhost:8877 ao iniciar

### Voice Management
✅ Gerenciamento de Vozes: Upload e gerenciamento de vozes customizadas
✅ Embeddings Cache: Pré-processamento para síntese mais rápida
✅ Voice Recording: Gravação de vozes diretamente pelo navegador (Web Audio API)

### Real-Time Features
✅ Monitor de Arquivo TXT: Síntese automática em tempo real
✅ Seleção de Voz Aleatória: Variação automática entre vozes
✅ Auto-play: Reprodução automática de áudio sintetizado
✅ Activity Log: Log de atividades com timestamps
✅ Sequential Playback: Reprodução ordenada de múltiplos áudios

### GPU Stability
✅ CUDA Error Recovery: Detecção e recuperação automática de erros GPU
✅ Device-side Assert Prevention: Validação de entrada para evitar crashes
✅ Async Thread Pool: Endpoints não-bloqueantes para responsividade

### Performance
✅ GPU Optimization: FP16 e quantização INT8 disponíveis
✅ Batch Processing: Suporte para múltiplas sínteses paralelas
✅ Model Caching: Modelos mantidos em memória

## 🎙️ Abas Disponíveis

1. **Dashboard** - Status do servidor e vozes disponíveis
2. **Síntese** - Sintetize texto com vozes disponíveis
   - Monitor de Arquivo TXT em tempo real
3. **Clonar Voz** - Crie vozes customizadas
4. **Gravar Voz** - Grave vozes usando o microfone
5. **Minhas Vozes** - Gerencie vozes salvass
6. **Configuração** - Limpeza de cache
7. **Sobre** - Idiomas suportados e API

## 🌐 Idiomas Suportados

- Português (pt)
- English (en)
- Español (es)
- Français (fr)
- Deutsch (de)
- Italiano (it)
- Polski (pl)
- Türkçe (tr)
- Русский (ru)
- Nederlands (nl)
- Čeština (cs)
- العربية (ar)
- 中文 (zh-cn)
- 日本語 (ja)
- Magyar (hu)
- 한국어 (ko)

## 🐛 Troubleshooting

### ModuleNotFoundError

Certifique-se de ativar o ambiente virtual:
\`\`\`bash
venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

### Porta 8877 em uso

Mude a porta em main.py (linha ~88):
\`\`\`python
PORT = 8878
\`\`\`

### GPU não detectada

Execute:
\`\`\`bash
install-cuda.bat
check_torch.py
\`\`\`

### Monitor de Arquivo não funciona

Verifique se o caminho do arquivo está correto e use caminhos absolutos:
\`\`\`
C:/Users/username/chat.txt
/home/username/messages.txt
\`\`\`

## 📊 API Endpoints Disponíveis

- \`POST /v1/synthesize\` - Sintetizar texto
- \`POST /v1/clone-voice\` - Clonar voz customizada
- \`POST /v1/voices/upload\` - Upload de voz
- \`POST /v1/monitor/read-file\` - Monitorar arquivo TXT
- \`GET /v1/voices\` - Listar vozes disponíveis
- \`DELETE /v1/voices/{voice_id}\` - Deletar voz
- \`GET /v1/info\` - Informações do servidor
- \`GET /health\` - Health check

## 📝 Versão

Release criado em: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

---

Para mais informações, consulte ENTREGA-COMPLETA.md
"@
    
    $readmePath = Join-Path $ReleaseDir "RELEASE-INFO.md"
    Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8
    Write-Status "README criado: RELEASE-INFO.md" Success
}

function Compress-ToZip {
    param([string]$ReleaseDir, [string]$OutputPath)
    
    Write-Status "Compactando em ZIP..." Process
    
    try {
        # Caminho do arquivo ZIP
        $zipPath = "$OutputPath.zip"
        
        # Usar Compress-Archive (nativo do PowerShell 5+)
        if (Test-Path $zipPath) {
            Remove-Item $zipPath -Force
        }
        
        Compress-Archive -Path $ReleaseDir -DestinationPath $zipPath -CompressionLevel Optimal
        
        $size = (Get-Item $zipPath).Length / 1MB
        Write-Status "ZIP criado: $(Split-Path -Leaf $zipPath) - $([math]::Round($size, 2)) MB" Success
        
        return $true
    }
    catch {
        Write-Status "Erro ao compactar ZIP: $_" Error
        return $false
    }
}

function Compress-To7z {
    param([string]$ReleaseDir, [string]$OutputPath)
    
    Write-Status "Compactando em 7z..." Process
    
    # Verificar se 7z está disponível
    $7zPath = Get-Command 7z -ErrorAction SilentlyContinue
    
    if (-not $7zPath) {
        Write-Status "7z não encontrado! Instale 7-Zip de https://www.7-zip.org/" Warn
        Write-Status "Ou coloque 7z.exe no PATH do sistema." Warn
        return $false
    }
    
    try {
        $archivePath = "$OutputPath.7z"
        
        if (Test-Path $archivePath) {
            Remove-Item $archivePath -Force
        }
        
        # Executar 7z
        & 7z a -t7z -m0=lzma2 -mx=9 -mfb=64 -md=32m -ms=on "$archivePath" "$ReleaseDir" | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            $size = (Get-Item $archivePath).Length / 1MB
            Write-Status "7z criado: $(Split-Path -Leaf $archivePath) - $([math]::Round($size, 2)) MB" Success
            return $true
        }
        else {
            Write-Status "Erro ao criar arquivo 7z (código: $LASTEXITCODE)" Error
            return $false
        }
    }
    catch {
        Write-Status "Erro ao compactar 7z: $_" Error
        return $false
    }
}

# ============================================================================
# MAIN
# ============================================================================

Clear-Host
Write-Status "=====================================================================" Info
Write-Status "SPEAKERBOT RELEASE CREATOR - ADVANCED (PowerShell)" Info
Write-Status "=====================================================================" Info

$projectDir = Get-Location
$timestamp = Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'
$releaseName = "Speakerbot-Release-$timestamp"
$releaseDir = Join-Path $projectDir $releaseName
$releasesFolder = Join-Path $projectDir "Releases"

Write-Status "Diretório do Projeto: $projectDir" Info
Write-Status "Nome do Release: $releaseName" Info
Write-Status "" Info

# Criar pasta Releases se não existir
if (-not (Test-Path $releasesFolder)) {
    New-Item -ItemType Directory -Path $releasesFolder -Force | Out-Null
}

# Loop de menu
while ($true) {
    Show-Menu
    
    if ($Option) {
        $choice = $Option
        $Option = $null  # Usar opção apenas uma vez
    }
    else {
        $choice = Get-MenuChoice
    }
    
    switch ($choice) {
        '1' {
            # Criar release simples
            Create-Release $releaseDir
            Write-Status "Release criado com sucesso em: $releaseDir" Success
            Write-Status "Pressione qualquer tecla para voltar..." Info
            Read-Host
            break
        }
        
        '2' {
            # Criar e compactar em ZIP
            Create-Release $releaseDir
            $outputPath = Join-Path $releasesFolder $releaseName
            Compress-ToZip $releaseDir $outputPath
            Write-Status "Pressione qualquer tecla para voltar..." Info
            Read-Host
            break
        }
        
        '3' {
            # Criar e compactar em 7z
            Create-Release $releaseDir
            $outputPath = Join-Path $releasesFolder $releaseName
            Compress-To7z $releaseDir $outputPath
            Write-Status "Pressione qualquer tecla para voltar..." Info
            Read-Host
            break
        }
        
        '4' {
            # Criar ambos
            Create-Release $releaseDir
            $outputPath = Join-Path $releasesFolder $releaseName
            Write-Status "" Process
            Compress-ToZip $releaseDir $outputPath
            Write-Status "" Process
            Compress-To7z $releaseDir $outputPath
            Write-Status "Pressione qualquer tecla para voltar..." Info
            Read-Host
            break
        }
        
        '5' {
            # Sair
            Write-Status "Encerrando..." Info
            exit 0
        }
    }
}
