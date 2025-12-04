# 🐧 Quick Start - Scripts Linux

## Instalação Rápida

### 1️⃣ Ativar Scripts
```bash
chmod +x scripts-linux/*.sh
```

### 2️⃣ Instalar SDK/Build Tools (primeira vez)
```bash
./scripts-linux/install-sdk-robust.sh
```

### 3️⃣ Instalar Dependências Python
```bash
./scripts-linux/install-deps-verbose.sh
```

### 4️⃣ Pronto! Agora você pode:
```bash
cd xtts-server
python3 start.py
```

---

## 🔧 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| `Permission denied` | `chmod +x scripts-linux/*.sh` |
| `Command not found: gcc` | `./scripts-linux/install-sdk-robust.sh` |
| `Python build tools missing` | `./scripts-linux/diagnose-sdk.sh` |
| Processos travados | `./scripts-linux/stop-build-processes.sh` |
| Alto CPU | `./scripts-linux/diagnose-cpu.sh` |
| Limpar cache git | `./scripts-linux/cleanup-git-cache.sh` |

---

## 📋 Referência Rápida

```bash
# Diagnosticar
./scripts-linux/diagnose-sdk.sh      # Verificar compiladores
./scripts-linux/diagnose-cpu.sh      # Verificar CPU

# Instalar
./scripts-linux/install-sdk-robust.sh   # Instalar build tools
./scripts-linux/install-deps-verbose.sh # Instalar Python deps

# Manutenção
./scripts-linux/stop-build-processes.sh # Matar processos
./scripts-linux/cleanup-git-cache.sh    # Limpar git

# Release
./scripts-linux/create-release-advanced.sh # Criar distribuição
```

---

## 🎯 Requisitos Mínimos

- **Linux:** Ubuntu 20.04+, Debian 11+, Fedora 36+, Arch, CentOS 8+
- **Python:** 3.10+
- **FFmpeg:** Para processamento de áudio
- **Compiladores:** GCC/Clang (instalado automaticamente)

---

## 📝 Documentação Completa

Para documentação detalhada, veja: `scripts-linux/README.md`

---

## ✅ Status

Todos os 8 scripts estão:
- ✅ Criados e testados
- ✅ Com permissões corretas
- ✅ Com documentação
- ✅ Prontos para produção
