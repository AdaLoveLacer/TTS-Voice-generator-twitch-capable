# Modos de Operação - TTS Voice Generator

## 🚀 Dois Modos Disponíveis

### Modo 1: Menu Interativo (Recomendado para Desenvolvimento)
**Arquivo:** `./menu.sh`

- Interface interativa com 17 opções
- Controle manual sobre cada etapa
- Ideal para troubleshooting e personalização
- Cria venv automaticamente na primeira execução

**Como usar:**
```bash
./menu.sh
```

**Opções disponíveis:**
1. Setup Rápido CachyOS 🔥
2. Validar Ambiente 🔍
3. Instalar Python 3.11 + Dependências ⭐
4. Instalar Dependências (Verbose)
5. Instalar Dependências (Inteligente)
6. Instalar SDK Robusto
7. **Corrigir PEP 668 (pip bloqueado) 🔧** ← Novo!
8. Criar Ambiente Virtual (venv)
9. Limpar Ambiente Virtual
10. Limpar Cache Git
11. Parar Processos de Build
12. Diagnosticar CPU
13. Diagnosticar SDK
14. Criar Release Avançado
15. Iniciar Servidor XTTS 🌐
16. Executar Script Customizado
17. Ver Ajuda
0. Sair

---

### Modo 2: Setup Automático (Novo - One-Click Setup)
**Arquivo:** `./run-auto.sh` ou `./auto-setup.sh`

- **Setup totalmente automático** em 5 etapas
- Cria venv, instala dependências, inicia servidor
- Em caso de erro, solicita ao usuário o que fazer
- Opções: tentar novamente, pular etapa ou cancelar

**Como usar:**
```bash
./run-auto.sh
```

**Etapas executadas automaticamente:**
1. **Validar Ambiente** - Verifica Python 3 e Python 3.11
2. **Configurar venv** - Cria/ativa ambiente virtual
3. **Instalar pip** - Recupera pip com fallbacks
4. **Instalar Dependências** - Instala requirements-linux.txt
5. **Iniciar Servidor** - Executa servidor XTTS

**Fluxo de Erro:**
```
Erro detectado ↓
Mostra mensagem de erro ↓
Oferece 3 opções:
  1) Tentar novamente
  2) Pular este passo
  3) Cancelar e sair
```

---

## 📊 Comparação dos Modos

| Aspecto | Menu Interativo | Setup Automático |
|---------|-----------------|------------------|
| **Facilidade** | Média | Máxima |
| **Controle** | Total | Automático com fallbacks |
| **Tempo** | Lento (manual) | Rápido (automático) |
| **Troubleshooting** | Excelente | Básico |
| **Ideal para** | Dev/Debug | Produção/Deploy |
| **venv** | Manual ou automático | Automático |

---

## 🔧 Recurso Novo: Corrigir PEP 668

O CachyOS/Arch bloqueia instalações no Python do sistema com erro:
```
error: externally-managed-environment
```

**Solução disponível na opção 7 do menu:**
```bash
./menu.sh → 7) Corrigir PEP 668 (pip bloqueado) 🔧
```

**Métodos de correção (em ordem):**
1. Instalar `python311-pip` via pacman
2. Usar ensurepip com `--break-system-packages`
3. Usar `get-pip.py` com `--break-system-packages`

---

## ⚡ Fluxo Recomendado

### Primeira Execução (Novo Usuário):
```bash
./run-auto.sh
# Tudo é feito automaticamente, servidor inicia no final
```

### Execuções Subsequentes:
```bash
source venv/bin/activate
./menu.sh → Opção 15 (Iniciar Servidor)
# ou
python3 xtts-server/start.py
```

### Em Caso de Problemas:
```bash
./menu.sh → Opção 7 (Corrigir PEP 668)
./menu.sh → Opção 2 (Validar Ambiente)
./menu.sh → Opção 3 (Reinstalar Dependências)
```

---

## 📝 Estrutura de Arquivos

```
.
├── menu.sh                    # Menu interativo manual (17 opções)
├── run-auto.sh               # Atalho para auto-setup
├── auto-setup.sh             # Setup automático completo
└── scripts-linux/
    ├── menu-interativo.sh    # Engine do menu (17 opções)
    ├── fix-pep668.sh         # Corretor de erro PEP 668
    ├── recover-pip-python311.sh
    ├── install-deps-python311.sh
    └── ... (outros scripts)
```

---

## 🎯 Próximos Passos

Após qualquer um dos setups, o servidor estará rodando em:
```
http://localhost:8000  (ou porta configurada)
```

Para acessar a interface web:
- Abra seu navegador
- Vá para `http://localhost:8000`

Para parar o servidor:
- Pressione `CTRL+C` no terminal

---

## 📞 Suporte

Se encontrar problemas:

1. **pip não funciona?**
   - Use opção 7 do menu: `Corrigir PEP 668`

2. **Dependências faltando?**
   - Use opção 3 do menu: `Instalar Python 3.11 + Dependências`

3. **Variáveis de ambiente?**
   - Use opção 2 do menu: `Validar Ambiente`

4. **Processos presos?**
   - Use opção 11 do menu: `Parar Processos de Build`
