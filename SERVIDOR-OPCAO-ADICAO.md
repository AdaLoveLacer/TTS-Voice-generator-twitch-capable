# Adição da Opção de Servidor - Resumo

## Alterações Realizadas

### 1. **Nova Função: `start_server()`**
   - Localização: Menu > Opção 14
   - Funcionalidade: Inicia o servidor XTTS
   - Comportamento:
     - Verifica se arquivo `start.py` existe no `xtts-server/`
     - Valida existência do ambiente virtual (venv)
     - Ativa o ambiente virtual
     - Executa `python3 start.py` no diretório do servidor
     - Desativa o ambiente virtual ao finalizar
     - Trata código de saída 130 (Ctrl+C) apropriadamente

### 2. **Menu Atualizado**
   - Nova seção: **SERVIDOR**
   - Opção: `14) Iniciar Servidor XTTS 🌐`
   - Deslocamento de opções:
     - Opção 14 (antes): Executar Script Customizado → agora opção 15
     - Opção 15 (antes): Ver Ajuda → agora opção 16
     - Opção 0 (antes): Sair → continua sendo opção 0

### 3. **Ajuda Atualizada**
   - Nova seção 3: **SERVIDOR**
     - Iniciar XTTS: Inicia o servidor de síntese de voz
   - Seção 4 (antes 3): **UTILITÁRIOS** (sem mudanças no conteúdo)

### 4. **Process Choice Atualizado**
   - Case statement agora possui 17 opções (1-16 + 0):
     ```bash
     14) start_server ;;
     15) select_custom_script ;;
     16) show_help ;;
     ```

## Estrutura do Menu Atual

```
┌─────────────────────────────────────────────────────┐
│ 🚀 TTS VOICE GENERATOR - MENU INTERATIVO LINUX 🚀 │
├─────────────────────────────────────────────────────┤
│ INSTALAÇÃO E DEPENDÊNCIAS:                          │
│   1) Setup Rápido CachyOS 🔥                        │
│   2) Validar Ambiente 🔍                            │
│   3) Instalar Python 3.11 + Dependências ⭐        │
│   4) Instalar Dependências (Verbose)                │
│   5) Instalar Dependências (Inteligente)            │
│   6) Instalar SDK Robusto                           │
│                                                     │
│ AMBIENTE VIRTUAL:                                   │
│   7) Criar Ambiente Virtual (venv)                  │
│   8) Limpar Ambiente Virtual                        │
│                                                     │
│ LIMPEZA E MANUTENÇÃO:                               │
│   9) Limpar Cache Git                               │
│   10) Parar Processos de Build                      │
│                                                     │
│ DIAGNÓSTICO:                                        │
│   11) Diagnosticar CPU                              │
│   12) Diagnosticar SDK                              │
│                                                     │
│ RELEASE:                                            │
│   13) Criar Release Avançado                        │
│                                                     │
│ SERVIDOR:        ← NOVO!                            │
│   14) Iniciar Servidor XTTS 🌐                      │
│                                                     │
│ UTILITÁRIOS:                                        │
│   15) Executar Script Customizado                   │
│   16) Ver Ajuda                                     │
│   0) Sair                                           │
└─────────────────────────────────────────────────────┘
```

## Pré-requisitos para Usar

1. **Ambiente virtual criado** (opção 7)
2. **Dependências instaladas** (opção 3 ou 1)
3. **Arquivo `xtts-server/start.py` presente**

## Tratamento de Erros

| Erro | Mensagem | Ação |
|------|----------|------|
| `start.py` não encontrado | `[X] Arquivo start.py não encontrado` | Volta ao menu |
| venv não existe | `[!] Ambiente virtual não encontrado` | Sugere criar venv |
| Servidor inicia normalmente | `✓ Servidor finalizado normalmente` | Aguarda Enter |
| Ctrl+C (130) | `ℹ Servidor interrompido pelo usuário` | Aguarda Enter |
| Outro erro | `✗ Servidor finalizado com erro: XX` | Aguarda Enter |

## Arquivos Modificados

- `/scripts-linux/menu-interativo.sh` - Adicionada função `start_server()` e opção no menu

## Validação

✓ Função `start_server()` criada e integrada
✓ Menu atualizado com nova opção 14
✓ Ajuda atualizada com seção SERVIDOR
✓ Números de opções ajustados corretamente
✓ Total de opções: 1-16 + 0 (17 opções)

## Como Usar

```bash
./menu.sh
# ou
./scripts-linux/menu-interativo.sh

# Selecionar opção 14 para iniciar o servidor
# O servidor continuará rodando até que você pressione Ctrl+C
```

## Características da Função `start_server()`

- ✅ Verifica pré-requisitos antes de iniciar
- ✅ Ativa/desativa ambiente virtual automaticamente
- ✅ Muda para diretório correto (xtts-server/)
- ✅ Restaura diretório após execução
- ✅ Trata diferentes códigos de saída
- ✅ Fornece feedback visual do estado
- ✅ Permite interrupção com Ctrl+C
