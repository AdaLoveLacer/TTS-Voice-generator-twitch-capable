# Changelog

Todas as mudanças notáveis deste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto segue [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [0.2.0] - 2025-11-29

### Adicionado
- 🌐 **Progressive Web App (PWA)** com suporte offline
  - Manifest.json para instalação como aplicativo
  - Service Worker com cache e sincronização
  - Suporte a notificações push
  - Shortcuts de acesso rápido

- 🎙️ **Rotas HTTP para servir web UI**
  - GET `/` - Serve web_ui.html
  - GET `/manifest.json` - Manifest PWA
  - GET `/service-worker.js` - Service Worker
  - Abertura automática do navegador ao iniciar

- 🛡️ **GPU Stability Improvements**
  - Detecção e recovery de device-side assert
  - Sanitização de áudio antes da síntese
  - Validação de arquivo WAV com tratamento de NaN/Inf
  - Retry automático com CUDA cache clearing

- 📊 **Sequential Playback**
  - Fila de áudio ordenada para múltiplas sínteses
  - Deduplicação com Set baseado em ID único
  - Apresentação visual do áudio em execução

### Melhorado
- ⚡ Performance: Endpoints assíncronos com thread pool
- 🔄 Async Processing: `run_in_threadpool` para operações bloqueantes
- 📝 Logging: Mensagens mais detalhadas sobre estado CUDA e síntese
- 🎨 UI: Indicador visual de configurações salvas
- 📁 Organização: Limpeza completa do projeto

### Corrigido
- 🐛 Backend freeze quando múltiplas requisições chegam simultaneamente
- 🐛 Duplicação de áudio na fila de reprodução
- 🐛 CUDA CUBLAS_STATUS_EXECUTION_FAILED com retry e recovery
- 🐛 CUDA device-side assert em arquivos WAV corrompidos
- 🐛 Tensor em GPU não sendo convertido para CPU antes de salvar

### Removido
- ❌ Arquivos de cache desnecessários
- ❌ Diretórios de desenvolvimento local (.vscode, .continue)
- ❌ Releases antigos do repositório
- ❌ Logs temporários

## [0.1.5] - 2025-11-19

### Adicionado
- Suporte para múltiplas referências de voz (1-5 arquivos WAV)
- Presets de configuração salvos automaticamente
- Monitor de arquivo TXT com síntese em tempo real
- Gravação de voz via Web Audio API
- 7 presets pré-configurados

### Melhorado
- Interface dark com efeitos neon
- Performance com embeddings cache
- Qualidade com GPT Cond Length customizável (3-30s)

### Corrigido
- Estabilidade da síntese em GPU

## [0.1.0] - 2025-11-01

### Adicionado
- Síntese multilíngue com XTTS v2
- Clonagem de voz com arquivo de referência
- Dashboard com status do servidor
- Upload de vozes customizadas
- Suporte a 16 idiomas
- API REST completa

---

## 📝 Notas de Versão

### Como Atualizar

```bash
git pull origin main
cd xtts-server
pip install -r requirements.txt
python main.py
```

### Quebras Compatíveis (Breaking Changes)

Nenhuma até o momento.

### Dependências Atualizadas

- TTS: 0.22.0 → 0.22.0
- PyTorch: 2.0+ (com suporte CUDA 11.8+)
- FastAPI: 0.104.0+

### Conhecidos Problemas

- Arquivos WAV muito longos (>5 minutos) podem causar timeout
- GPU com <8GB VRAM pode ter problemas com batch processing
- Requer Python 3.11+

---

## Próximas Versões (Roadmap)

### v0.3.0 (Planejado)
- [ ] Suporte para StyleTTS2 e VITS como engines opcionais
- [ ] Sistema de seleção de motor TTS via UI
- [ ] Melhorias de UI/UX
- [ ] Documentação expandida

### v0.4.0 (Planejado)
- [ ] API Authentication
- [ ] WebSocket real-time
- [ ] Rate limiting
- [ ] Métricas e monitoramento

---

Para reportar bugs ou sugerir features, abra uma [issue no GitHub](https://github.com/seu-usuario/Speakerbot-local-voice/issues).
