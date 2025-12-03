# Instalação de TTS no Windows

## Problema

Ao tentar instalar TTS (`pip install TTS`), recebe erro:
```
fatal error C1083: Não é possível abrir arquivo incluir: 'io.h': No such file or directory
```

Este erro ocorre porque **TTS requer compilação C++** e o Windows SDK não está instalado.

## Solução

### Opção 1: Visual Studio Build Tools 2022 (Recomendado)

1. Acesse: https://visualstudio.microsoft.com/downloads/
2. Role para baixo até "All Downloads"
3. Clique em "Visual Studio Build Tools 2022"
4. Execute o instalador baixado
5. Na janela de seleção de componentes:
   - Marque **"Desktop development with C++"**
   - Clique em **"Install"**
6. Aguarde a instalação (pode levar 10-30 minutos)
7. Reinicie o computador se necessário

### Opção 2: Windows 11 SDK

1. Acesse: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
2. Clique em "Download Windows 11 SDK"
3. Execute o instalador
4. Selecione os componentes de SDK
5. Clique em "Install"

### Pós-Instalação

Após instalar, execute:

```bash
# Com Python 3.11 (recomendado)
py -3.11 start.py install

# Ou com start.py interativo
py -3.11 start.py
# Escolha opção 1: Instalar
```

## Verificação

Para verificar se o SDK está instalado corretamente:

```bash
# Procure por io.h
where io.h
# Ou procure manualmente em:
# C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.xx.xxxxx\include
```

## Troubleshooting

### Erro: "Python 3.11 não encontrado"

Instale Python 3.11 de: https://www.python.org/downloads/

Você pode ter múltiplas versões de Python no Windows. A instalação recomenda selecionar:
- "Add Python 3.11 to PATH"

### Erro: "Failed to build TTS"

1. Verifique se o Visual Studio Build Tools está instalado
2. Abra "Visual Studio Installer"
3. Clique em "Modify" ao lado do Build Tools
4. Verifique se "C++ Build Tools" está marcado
5. Se não estiver, marque e clique "Install"

### Erro: "winget is not recognized"

O comando `winget` (Windows Package Manager) pode não estar disponível em versões antigas do Windows 10.

Use a instalação manual via navegador (links acima).

## Próximas Etapas

Após instalar o Windows SDK e TTS compilar com sucesso:

```bash
# Iniciar servidor
py -3.11 start.py 3

# Ou use menu interativo
py -3.11 start.py
# Escolha 3: Iniciar servidor
```

O servidor estará disponível em: http://localhost:8000
Documentação da API: http://localhost:8000/docs

## Performance Notes

- **Primeira execução**: Pode levar 5-10 minutos para baixar modelos de TTS
- **CUDA**: Acelera significativamente o processamento (instalado automaticamente com PyTorch 2.7.1+cu118)
- **CPU**: Funcionará mas será mais lento

## Suporte

Se continuar tendo problemas, verifique:

1. Python version: `py -3.11 --version` (deve ser 3.11.x)
2. Compilador: `cl.exe /?` (deve reconhecer)
3. Setup.py: `py -3.11 -c "import distutils.core; print(distutils.core.__file__)"`

