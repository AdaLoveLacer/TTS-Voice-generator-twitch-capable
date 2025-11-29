# 🚀 Quick Start Guide

Guia rápido e universal para todas as plataformas (Windows, Linux, macOS).

## Windows

### Setup Automático (Recomendado)
```batch
cd xtts-server
start-server.bat
```

**O que faz:**
1. ✅ Cria venv se não existir
2. ✅ Ativa venv
3. ❓ Menu: Reinstalar CUDA? (escolha 1 ou 2)
4. ✅ Instala dependências
5. ✅ Inicia servidor
6. 🌐 Abre navegador em `http://localhost:8877`

### Setup Automático (Sem Menu)
```batch
cd xtts-server
start-server-auto.bat
```

### Instalar/Reinstalar CUDA
```batch
cd xtts-server
install-cuda.bat
```

---

## Linux / macOS

### Setup Automático (Recomendado)
```bash
cd xtts-server
chmod +x *.sh
./start-server.sh
```

### Setup Automático (Sem Menu)
```bash
cd xtts-server
chmod +x *.sh
./start-server-auto.sh
```

### Instalar/Reinstalar CUDA
```bash
cd xtts-server
chmod +x *.sh
./install-cuda.sh
```

---

## Todas as Plataformas

### Iniciar Manual (sem script)
```bash
# 1. Criar venv (primeira vez)
python -m venv venv

# 2. Ativar venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instalar deps
pip install -r requirements.txt

# 4. Iniciar servidor
python main.py
```

### Parar o Servidor
```
Pressione: CTRL+C
```

### Acessar Interface
```
Navegador: http://localhost:8877
API Docs: http://localhost:8877/docs
Health: http://localhost:8877/v1/health
```

---

## 🆘 Troubleshooting

### Python não encontrado
```bash
# Verificar
python --version
# ou
python3 --version

# Instalar: https://www.python.org/downloads/
```

### "Permission denied" em Linux/macOS
```bash
chmod +x *.sh
```

### Erro ao criar venv
```bash
rm -rf venv
# Executar script novamente
```

### CUDA não encontrado
```bash
# Se tem GPU NVIDIA:
# Windows: install-cuda.bat
# Linux/macOS: ./install-cuda.sh

# Se não tem GPU: Funcionará em CPU
```

### Porta 8877 ocupada
```bash
# Editar main.py linha 89:
PORT = 8878  # Mudar porta
```

---

## 📊 Estrutura

```
xtts-server/
├── start-server.bat/.sh
├── start-server-auto.bat/.sh
├── install-cuda.bat/.sh
├── main.py
├── web_ui.html
├── requirements.txt
└── venv/  (criado automaticamente)
```

---

## 💡 Dicas

**Usar frequentemente?**
- Windows: Atalho para `start-server.bat`
- Linux/macOS: Alias no `.bashrc`:
  ```bash
  alias speakerbot='cd ~/...xtts-server && ./start-server.sh'
  ```

**Primeira execução é lenta?**
- ✅ Normal! Modelo TTS (~2GB) é baixado uma vez
- Próximas execuções são muito mais rápidas

**Múltiplas abas/janelas?**
- ✅ Funciona! Servidor suporta múltiplas conexões

---

## 🚀 Próximos Passos

1. Execute o script
2. Aguarde inicialização (5-10 min primeira vez)
3. Abra `http://localhost:8877`
4. Divirta-se! 🎙️

**Precisa de ajuda?**
- GitHub Issues
- `/docs` - Documentação
- `CONTRIBUTING.md` - Guidelines

**Última atualização**: 29/11/2025
