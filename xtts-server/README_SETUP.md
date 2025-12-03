# XTTS Server - Guia de Instalação e Uso

## 📋 Requisitos

- **Windows 10/11**
- **Python 3.11** (recomendado) ou 3.10
- **Visual Studio Build Tools 2022** (para compilar TTS)
  - OU **Windows 11 SDK**
- **Espaço em disco**: ~20GB (para modelos TTS + PyTorch)

## 🚀 Quick Start

### 1. Verificar Python 3.11

```bash
py -3.11 --version
# Python 3.11.0
```

Se não reconhecer, instale de: https://www.python.org/downloads/

### 2. Instalar Windows SDK

Siga o guia em: [INSTALL_SDK.md](./INSTALL_SDK.md)

Este é o passo **mais crítico** - sem ele, TTS não compilará.

Você pode tentar usar o instalador automático incluído no projeto:

```powershell
py -3.11 install-sdk.py
```

O script tentará `winget`/`choco` e, se necessário, baixará o instalador do Visual Studio Build Tools e recriará o processo com privilégios de Administrador.

### 3. Instalar Dependências

```bash
# Com venv limpo
py -3.11 start.py install

# Ou menu interativo
py -3.11 start.py
# Escolha: 1 (Instalar)
```

**Tempo estimado**: 10-20 minutos (primeira vez, inclusive downloads)

### 4. Verificar Bibliotecas

```bash
py -3.11 start.py 2
# Ou no menu: 2 (Verificar libs)
```

Deve listar todas as dependências instaladas com sucesso.

### 5. Iniciar Servidor

```bash
py -3.11 start.py 3
# Ou no menu: 3 (Servidor)

# Acesse:
# http://localhost:8000        (Web UI)
# http://localhost:8000/docs   (API Documentation)
```

## 📖 Uso do start.py

### Menu Interativo

```bash
py -3.11 start.py
```

Opções:
- **1 = Instalar** - Cria venv e instala todas as dependências
- **2 = Verificar** - Lista bibliotecas instaladas
- **3 = Servidor** - Inicia o servidor FastAPI
- **4 = Limpar** - Remove venv e cache (para fresh start)
- **5 = Sair**

### Modo CLI

```bash
# Instalar
py -3.11 start.py install
py -3.11 start.py 1

# Verificar
py -3.11 start.py check
py -3.11 start.py 2

# Servidor
py -3.11 start.py server
py -3.11 start.py 3

# Limpar e reinstalar
py -3.11 start.py clean
py -3.11 start.py 4

### Skipping TTS compilation (if you don't want to compile TTS/SDK is missing)

If you don't have the Windows SDK installed or prefer to skip compiling the TTS package, pass the `--skip-tts` flag or set the environment variable:

```bash
py -3.11 start.py install --skip-tts
# or
set XTTS_SKIP_TTS=1
py -3.11 start.py install

### Install only TTS

Se você deixou o TTS de fora na instalação inicial ou preferir instalar o TTS separadamente depois de instalar o Windows SDK, use o comando dedicado:

```bash
# Instala somente o pacote TTS (requer SDK/MSVC configurado):
py -3.11 start.py install-tts

# Forçar reinstalação:
py -3.11 start.py install-tts --force

# Se você tem problemas com build-isolation use:
py -3.11 start.py install-tts --no-build-isolation
```

### Install StyleTTS2 (motor TTS alternativo)

StyleTTS2 é um motor TTS alternativo que é **2-3x mais rápido** que XTTS v2 mas com qualidade ligeiramente menor. Instale opcionalmente:

```bash
# Instalar StyleTTS2:
py -3.11 start.py install-styletts2

# Forçar reinstalação:
py -3.11 start.py install-styletts2 --force
```

Depois que StyleTTS2 estiver instalado, você pode selecioná-lo na interface web quando sintetizar texto.
```
```

## 🔧 Troubleshooting

### "io.h: No such file or directory"

**Causa**: Windows SDK não instalado

**Solução**: Siga [INSTALL_SDK.md](./INSTALL_SDK.md)

### "Python 3.11 não encontrado"

**Causa**: Python 3.11 não está no PATH

**Solução**:
1. Instale de: https://www.python.org/downloads/
2. Marque "Add Python 3.11 to PATH"
3. Reinicie o terminal

### "TTS not found" ao iniciar servidor

**Causa**: TTS não compilou (provavelmente falta Windows SDK)

**Solução**:
```bash
# Limpar e reinstalar
py -3.11 start.py 4
```

### Erro de permissão ao criar venv

**Causa**: Windows bloqueando acesso à pasta

**Solução**:
1. Feche VS Code
2. Execute como Administrator:
   ```bash
   py -3.11 start.py 4
   ```
3. Reabra VS Code

### Servidor lento/congelado

**Causa**: Processamento em CPU (sem CUDA)

**Verificar**:
```bash
py -3.11 -c "import torch; print(torch.cuda.is_available())"
# True = CUDA ativo (rápido)
# False = Usando CPU (lento)
```

Se CUDA não está disponível, o servidor ainda funcionará mas mais lentamente.

### VS Code/Terminal consumindo 100% CPU após instalação

**Causa**: Processos de compilação (cl.exe, python.exe) travados

**Solução rápida**:
1. Execute em um novo terminal PowerShell:
   ```powershell
   cd G:\VSCODE\Speakerbot-local-voice\xtts-server
   py -3.11 start.py diagnose-cpu
   ```
2. Selecione "s" para parar os processos problemáticos
3. Feche e reabra o VS Code

**Se persistir**:
```powershell
# Parar todos os processos de build imediatamente:
py -3.11 start.py stop-processes

# Depois, limpar cache e venv corrompido:
py -3.11 start.py cleanup-stuck
```

**Último recurso**:
- Reinicie o Windows
- Abra um novo terminal PowerShell
- Execute: `py -3.11 start.py install`

## 📁 Estrutura do Projeto

```
xtts-server/
├── main.py                 # FastAPI server principal
├── start.py               # Launcher e gerenciador de venv
├── requirements.txt       # Dependências Python
├── INSTALL_SDK.md        # Guia Windows SDK (TTS compilation)
├── README_SETUP.md       # Este arquivo
├── venv/                 # Virtual environment (criado automaticamente)
├── .pip-cache/          # Cache local de pacotes pip
├── engines/             # Implementação de engines TTS
├── voices/              # Modelos de vozes
└── web_ui.html         # Interface web
```

## 🌐 API Endpoints

Documentação completa em: http://localhost:8000/docs

### Exemplos

**Síntese de texto**:
```bash
curl -X POST http://localhost:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Olá mundo", "language": "pt"}'
```

**Clonagem de voz**:
```bash
curl -X POST http://localhost:8000/clone_voice \
  -F "audio=@voice_sample.wav" \
  -F "text=Nova voz clonada"
```

## 🎯 Performance

**Requisitos mínimos**:
- CPU: 4 cores
- RAM: 8GB
- GPU: Opcional (10x mais rápido)

**Tempo de processamento**:
- CPU: ~10s para 1 minuto de áudio
- GPU (CUDA): ~1s para 1 minuto de áudio
- Primeira execução: +5-10min (download de modelos)

## 📝 Notas Importantes

1. **Primeira execução**: Pode levar tempo porque os modelos de TTS (~1GB) são baixados automaticamente
2. **Cache**: Todos os pacotes pip são armazenados em `.pip-cache/` (dentro do projeto)
3. **Python 3.11**: Recomendado para evitar problemas de compatibilidade com setuptools
4. **Offline**: Depois da primeira execução, o servidor pode rodar offline se não precisar de novos modelos

## 🚨 Quando Limpar Tudo

Execute se tiver problemas de dependência:

```bash
py -3.11 start.py clean
py -3.11 start.py install
```

Isso removerá:
- `venv/` - Virtual environment completo
- `.pip-cache/` - Cache de pacotes

## ✅ Checklist de Setup

- [ ] Python 3.11 instalado (`py -3.11 --version`)
- [ ] Visual Studio Build Tools 2022 instalado (com C++)
- [ ] Repositório clonado/baixado
- [ ] Terminal aberto na pasta `xtts-server/`
- [ ] Executou `py -3.11 start.py install`
- [ ] Verificou `py -3.11 start.py check` (sem erros)
- [ ] Iniciou `py -3.11 start.py server`
- [ ] Acessou http://localhost:8000 no navegador

## 📞 Suporte

Se encontrar problemas:

1. Verifique o erro completo na pasta `venv/`
2. Tente limpar e reinstalar: `py -3.11 start.py 4`
3. Consulte [INSTALL_SDK.md](./INSTALL_SDK.md) para problemas de compilação

