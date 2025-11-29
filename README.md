# Speakerbot - Síntese de Voz Local

Servidor Text-to-Speech (TTS) local baseado em XTTS v2. Converte texto em áudio de alta qualidade, com suporte a clonagem de voz, 16 idiomas e interface web moderna.

> 📚 **Documentação Completa**: Toda documentação foi reorganizada em [`/docs`](docs/). Comece em [`docs/QUICK_START.md`](docs/QUICK_START.md) para guia rápido ou [`docs/README.md`](docs/README.md) para navegação completa.

## O Que É

Aplicativo que gera fala profissional a partir de texto. Funciona completamente offline em sua máquina com GPU NVIDIA. Inclui interface web, API REST e suporte a OBS Studio.

## Recursos Principais

- **Síntese de Voz**: Texto para áudio de alta qualidade (24kHz)
- **Clonagem de Voz**: Crie vozes personalizadas (1-5 arquivos de referência)
- **16 Idiomas**: Português, English, Español, Français, Deutsch, Italiano, Polski, Türkçe, Русский, Nederlands, Čeština, العربية, 中文, 日本語, Magyar, 한국어
- **Interface Web**: Navegador em `http://localhost:8877`
- **API REST**: Integração com outras aplicações
- **Monitor de Arquivo**: Sintetize linhas de um TXT automaticamente
- **Fila Sequencial**: Processa múltiplas requisições uma por uma
- **OBS Streaming**: Transmita áudio direto para OBS Studio
- **PWA**: Instale como aplicativo nativo

## Requisitos

- **GPU NVIDIA**: RTX 3050+ com mínimo 4GB VRAM (**TESTADO EM** RTX 3060 com 12GB )
- **Python**: 3.10+
- **CUDA**: 11.8+
- **cuDNN**: 8.x
- **RAM**: 8GB mínimo (16GB recomendado)
- **Disco**: 5GB para modelos

**Nota**: Apenas GPU NVIDIA suportada. CPU é impraticável (~5 minutos por síntese).

## Instalação

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/Speakerbot-local-voice.git
cd Speakerbot-local-voice/xtts-server
```

### 2. Configure o Ambiente

**Windows:**
```bash
# Duplo-clique em start-server.bat (automático)
# ou
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
cd xtts-server
chmod +x *.sh
./start-server.sh
```

### 3. Instale Dependências

**Automático (recomendado):**
- Windows: `start-server.bat`
- Linux/macOS: `./start-server.sh`

**Manual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 4. Inicie o Servidor

**Automático:**
- Windows: Duplo-clique em `start-server.bat` ou `start-server-auto.bat`
- Linux/macOS: `./start-server.sh` ou `./start-server-auto.sh`

**Manual:**
```bash
python main.py
```

Acesse: **http://localhost:8877**

---

**Nota sobre CUDA:** Se você tem GPU NVIDIA e quer usar CUDA:
- Windows: `install-cuda.bat` (ou menu no `start-server.bat`)
- Linux/macOS: `./install-cuda.sh` (ou menu no `start-server.sh`)

## Como Usar

### Interface Web

1. Abra `http://localhost:8877`
2. Digite seu texto
3. Escolha idioma e voz
4. Clique em "Sintetizar"
5. Ouça ou baixe o áudio

### Clonar Voz

1. Prepare 1-5 arquivos WAV com sua voz (10-30 segundos cada)
2. Vá para aba "Clonar Voz"
3. Faça upload dos arquivos
4. Digite o texto a sintetizar
5. Clique em "Criar Voz"

### Monitorar Arquivo TXT

1. Crie um arquivo `monitor.txt`
2. Vá para aba "Monitor"
3. Selecione o arquivo
4. Adicione linhas ao arquivo - cada linha será sintetizada automaticamente
5. Audios reproduzem em fila ordenada

### OBS Studio

1. No servidor Speakerbot, vá para "Configurações → OBS"
2. Copie a URL do player invisível
3. No OBS: **Sources → + → Browser**
4. Cole a URL
5. Configure: 1x1 pixels (invisível)
6. Áudio transmitido automaticamente

## API REST

### Sintetizar Texto

```bash
curl -X POST "http://localhost:8877/v1/synthesize" \
  -F "text=Olá mundo" \
  -F "language=pt" \
  -F "voice=default" \
  -F "speed=1.0"
```

Parâmetros:
- `text`: Texto a sintetizar
- `language`: Código de idioma (pt, en, es, etc)
- `voice`: Nome da voz (default ou customizada)
- `speed`: Velocidade (0.5 a 2.0)
- `temperature`: Variabilidade (0.1 a 1.0)

Resposta:
```json
{
  "success": true,
  "audio": "base64_encoded_audio"
}
```

### Clonar Voz

```bash
curl -X POST "http://localhost:8877/v1/clone-voice" \
  -F "text=Meu texto" \
  -F "language=pt" \
  -F "speaker_wav=@ref1.wav" \
  -F "speaker_wav=@ref2.wav"
```

### Listar Vozes

```bash
curl "http://localhost:8877/v1/voices"
```

### Monitorar com Fila

```bash
curl -X POST "http://localhost:8877/v1/monitor/process-queue" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/file.txt"}'
```

### Status da Fila

```bash
curl "http://localhost:8877/v1/queue/status?context_id=monitor_%2Fpath%2Fto%2Ffile.txt"
```

Mais detalhes: [Documentação completa da API](docs/api/README.md)

## Configuração

### Variáveis de Ambiente

```bash
# GPU/Device
XTTS_DEVICE=cuda  # 'cuda' ou 'cpu'

# Servidor
PORT=8877
HOST=127.0.0.1

# Cache
PIP_CACHE_DIR=.pip-cache
```

### Parâmetros de Síntese (Web UI)

- **Velocidade**: 0.5x a 2.0x
- **Temperatura**: 0.1 a 1.0 (variabilidade)
- **Top-K**: 0 a 100
- **Top-P**: 0.0 a 1.0
- **Duração**: 3 a 30 segundos
- **Escala**: 0.5x a 2.0x

## Performance

### Benchmark (RTX 3060 com 12GB VRAM)

| Tarefa | Tempo | Qualidade |
|--------|-------|-----------|
| Síntese 10s | 2-3s | 24kHz |
| Clonagem de voz | 5-8s | Com referência |
| Batch 5 textos | 8-12s | Sequencial |

### Recomendações

| GPU | VRAM | Adequado Para |
|-----|------|--------|
| RTX 3060 | 12GB | Uso geral |
| RTX 4070 | 12GB | Batch processing |
| RTX 4090 | 24GB | Produção |

## Problemas Comuns

### ModuleNotFoundError: TTS

```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### CUDA Error: device-side assert triggered

```bash
python -c "import torch; torch.cuda.empty_cache()"
```

### GPU Não Detectada

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

### Porta 8877 em Uso

Edite `xtts-server/main.py` linha ~88:
```python
PORT = 8878
```

## Estrutura do Projeto

```
xtts-server/
├── main.py              # Servidor FastAPI
├── voice_manager.py     # Gerenciamento de vozes
├── speaker_embedding_manager.py  # Embeddings de clonagem
├── web_ui.html          # Interface web
├── voices/              # Vozes customizadas
├── requirements.txt     # Dependências
└── start-server.bat     # Script Windows
```

## Casos de Uso

- **Audiobooks**: Gere áudio profissional para livros
- **Dubagem de Vídeo**: Crie vozes sincronizadas com vídeo
- **Assistentes de Voz**: Integre em bots ou aplicações
- **Streaming Live**: Transmita áudio para OBS/Twitch
- **Documentários**: Narração automática

## Tecnologias

- **XTTS v2**: Engine TTS multilíngue (Coqui)
- **FastAPI**: Framework web assíncrono
- **PyTorch**: Machine learning com CUDA
- **NumPy/SciPy**: Processamento de áudio
- **HTML5/CSS3/JS**: Interface web moderna

## Limitações

- Apenas GPU NVIDIA com CUDA suportada
- Máximo ~30 segundos por síntese
- Requer GPU com 4GB+ VRAM
- Não funciona com áudio protegido/DRM
- Apenas texto ASCII/Unicode

## Desenvolvimento

### Requisitos Dev

```bash
pip install pytest pylint black
```

### Testes

```bash
pytest tests/
```

### Linting

```bash
pylint xtts-server/*.py
black xtts-server/
```

## 📚 Documentação

Toda documentação está organizada em [`/docs`](docs/):

| Documento | Descrição |
|-----------|-----------|
| [Quick Start](docs/QUICK_START.md) | Setup em 3 passos |
| [Setup Linux/macOS](docs/setup/LINUX_MACOS_SETUP.md) | Guia para Linux/macOS |
| [Troubleshooting](docs/QUICK_START.md#troubleshooting) | Soluções de problemas |
| [Contributing](docs/CONTRIBUTING.md) | Como contribuir |
| [Changelog](docs/CHANGELOG.md) | Histórico de versões |
| [GitHub Setup](docs/GITHUB_SETUP.md) | Publicação no GitHub |
| [Status do Projeto](docs/GITHUB_READINESS_REPORT.md) | Score 97/100 |
| [Índice Completo](docs/INDEX.md) | Navegação por caso de uso |

## Créditos

- **XTTS v2** - Coqui AI
- **FastAPI** - Sebastián Ramírez
- **PyTorch** - Meta AI

## Licença

MIT License - veja [LICENSE](LICENSE)

## Suporte

- Issues: [GitHub Issues](https://github.com/seu-usuario/Speakerbot-local-voice/issues)
- Email: seu-email@exemplo.com

---

*Última atualização: 2025*
