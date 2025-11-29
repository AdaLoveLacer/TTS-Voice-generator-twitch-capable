# 🎙️ OBS Audio Streaming - Guia de Configuração

## 📋 Visão Geral

O Speakerbot agora suporta streaming de áudio em tempo real para o **OBS Studio** (Open Broadcaster Software) sem necessidade de interface visual. Isso permite que você transmita TTS (Text-to-Speech) sintetizado diretamente para suas streams ao vivo.

## ✨ Recursos

- ✅ **Sem UI**: Player de áudio invisível (1x1 pixel)
- ✅ **Streaming em Tempo Real**: Áudio sintetizado é enviado automaticamente para OBS
- ✅ **WebSocket**: Conexão bidirecional para comunicação eficiente
- ✅ **Auto-reconexão**: Reconecta automaticamente se a conexão cair
- ✅ **Múltiplas Conexões**: Suporta múltiplos clientes OBS conectados simultaneamente

## 🚀 Como Configurar

### Passo 1: Obter a URL de Configuração

Acesse a rota de configuração do OBS:

```
GET http://localhost:8877/obs-config
```

Resposta exemplo:
```json
{
  "audio_player_url": "http://localhost:8877/obs-audio",
  "websocket_url": "ws://localhost:8877/ws/audio",
  "active_connections": 0,
  "instructions": {
    "pt": "1. Copie a URL do audio_player_url...",
    "en": "1. Copy the audio_player_url..."
  }
}
```

### Passo 2: Adicionar Browser Source no OBS

1. **Abra o OBS Studio**
2. Na seção **Sources**, clique em **+** (Adicionar)
3. Selecione **Browser** (Navegador)
4. Dê um nome (ex: "Speakerbot Audio")
5. Clique em **Create New**

### Passo 3: Configurar a Browser Source

Na janela de propriedades da Browser Source:

1. **URL**: Cole a URL do `audio_player_url`
   ```
   http://localhost:8877/obs-audio
   ```

2. **Largura (Width)**: `1`
3. **Altura (Height)**: `1`
4. ✅ Marque: **Controlar áudio via OBS** (ou similar)
5. Clique em **OK**

### Passo 4: Testar

1. Use a interface web do Speakerbot em `http://localhost:8877`
2. Sintetize um texto qualquer
3. O áudio deve reproduzir automaticamente no OBS

## 📡 API Endpoints

### GET `/obs-audio`
Player de áudio compatível com OBS (sem UI visível).

**Resposta**: HTML com player de áudio + WebSocket client

### GET `/obs-config`
Retorna configuração e instruções de setup.

**Query Parameters**:
- `request_url` (opcional): URL customizada para o player (se não for localhost)

**Resposta**:
```json
{
  "audio_player_url": "http://localhost:8877/obs-audio",
  "websocket_url": "ws://localhost:8877/ws/audio",
  "instructions": {...},
  "active_connections": 1,
  "features": {
    "real_time_streaming": true,
    "audio_only": true,
    "no_ui_required": true,
    "auto_reconnect": true
  }
}
```

### WS `/ws/audio`
WebSocket para streaming de áudio em tempo real.

**Mensagens Recebidas**:
```json
{
  "type": "audio",
  "audio": "base64_encoded_wav_data",
  "timestamp": "2024-11-29T10:30:45.123456"
}
```

## 🎬 Fluxo de Funcionamento

```
┌─────────────────────────────────────────────────┐
│        Speakerbot Web UI                        │
│  (http://localhost:8877)                        │
│                                                  │
│  Usuário sintetiza texto → /v1/synthesize       │
└────────────────┬────────────────────────────────┘
                 │
                 ├─→ Síntese de áudio (XTTS v2)
                 │
                 ├─→ Salva WAV temporário
                 │
                 └─→ Broadcast para WebSocket
                         │
                         ├─→ OBS Browser Source
                         │   (ws://localhost:8877/ws/audio)
                         │
                         └─→ Player reproduz áudio
                             (automático no OBS)
```

## 🔧 Troubleshooting

### "Não ouço áudio no OBS"

1. ✅ Verifique se o server XTTS está rodando:
   ```bash
   http://localhost:8877/v1/info
   ```

2. ✅ Verifique a URL da Browser Source:
   - Deve ser: `http://localhost:8877/obs-audio`
   - Não coloque `ws://` ou `wss://` aqui

3. ✅ Verifique o console do navegador (F12 no OBS):
   - Pressione Ctrl+Shift+I no OBS
   - Veja se há erros de conexão WebSocket

4. ✅ Firewall/Rede:
   - Se OBS e Speakerbot estão em máquinas diferentes:
   ```
   GET http://SEU_IP:8877/obs-config?request_url=http://SEU_IP:8877
   ```

### "WebSocket não conecta"

1. Verifique se a porta 8877 está acessível
2. Se usa proxy/firewall, libere a porta
3. Reinicie o OBS

## 💡 Dicas de Uso

### Multi-Streaming
Você pode ter múltiplas Browser Sources do Speakerbot em diferentes Scenes:

```
Scene "Transmissão"
├─ Browser Source 1: Speakerbot Audio
├─ Browser Source 2: Outro aplicativo
└─ ...
```

Todos receberão o áudio sintetizado automaticamente.

### Áudio com Volume Controlável
No OBS, você pode:
- Ajustar o volume do áudio na mixer de áudio
- Mutar/desmutar conforme necessário
- Adicionar efeitos de áudio

### Integração com OBS Scripts
Você pode criar scripts LUA/Python para o OBS que disparem síntese via HTTP:

```lua
-- Exemplo LUA para OBS
function synthesize_and_play(text)
    local url = "http://localhost:8877/v1/synthesize"
    -- POST request com o texto
end
```

## 🌐 Setup em Rede

Se o OBS está em outra máquina:

### Passo 1: Altere o HOST do servidor

No `start-server.bat`:
```batch
python main.py --host 0.0.0.0 --port 8877
```

### Passo 2: Configure a URL

Na Browser Source do OBS:
```
http://SEU_IP_LOCAL:8877/obs-audio
```

### Exemplo
```
http://192.168.1.100:8877/obs-audio
```

## 📊 Status de Conexões

Para monitorar conexões ativas:

```bash
curl http://localhost:8877/obs-config
```

Resposta incluirá:
```json
"active_connections": 2
```

## 🔐 Segurança

- ⚠️ **Não exponha para Internet**: Use apenas em rede local
- ⚠️ **Firewall**: Restrinja a porta 8877 ao localhost se possível
- ℹ️ Nenhuma autenticação implementada (para rede local)

## 📝 Exemplos de Integração

### Python + OBS
```python
import requests

def send_to_speakerbot(text, language="pt", voice="default"):
    """Enviar síntese para OBS"""
    url = "http://localhost:8877/v1/synthesize"
    data = {
        "text": text,
        "language": language,
        "voice": voice,
        "speed": 1.0,
        "temperature": 0.75
    }
    response = requests.post(url, data=data)
    return response.content  # Audio WAV
```

### JavaScript + OBS
```javascript
async function synthesizeAndPlay(text) {
    const formData = new FormData();
    formData.append("text", text);
    formData.append("language", "pt");
    formData.append("voice", "default");
    
    const response = await fetch("http://localhost:8877/v1/synthesize", {
        method: "POST",
        body: formData
    });
    
    // Audio é automaticamente enviado para OBS via WebSocket
}
```

## 🚀 Performance

- **Latência de Áudio**: ~100-500ms (dependendo do comprimento do texto)
- **Conexões Simultâneas**: Suporta ilimitado (limitado pela RAM)
- **Bandwidth**: ~128-256 kbps por conexão (WAV PCM)

## 📚 Recursos Adicionais

- [Documentação OBS Browser Source](https://obsproject.com/wiki/Plugins/BrowserSource)
- [API Speakerbot](/v1/info)
- [WebSocket API Spec](/obs-config)

---

**Versão**: 0.2.0  
**Última Atualização**: 29 de Novembro de 2024  
**Suporte**: GitHub Issues ou Discussões do Projeto
