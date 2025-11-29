PIP Cache e Temp local do projeto

Objetivo:
- Forçar que o `pip` use diretórios de cache e diretório temporário dentro da pasta do projeto (`.pip-cache` e `.pip-tmp`) para evitar ocupar o disco `C:` do sistema.

O que foi feito:
- `start-server.bat` agora define `PIP_CACHE_DIR` e `TMP/TEMP` apontando para `.pip-cache` e `.pip-tmp` na raiz de `xtts-server` antes de executar instalações. O script cria essas pastas automaticamente.
- Os scripts de ativação do venv foram modificados:
  - `venv\Scripts\activate.bat` — define `PIP_CACHE_DIR`, `TMP` e `TEMP` ao ativar o venv no prompt do Windows.
  - `venv\Scripts\Activate.ps1` — define `PIP_CACHE_DIR`, `TMP` e `TEMP` ao ativar o venv no PowerShell.

Como usar:
- Se você usa o `start-server.bat` normalmente, tudo já está configurado. O script criará `.pip-cache` e `.pip-tmp` e usará essas pastas para `pip install`.

- Se você ativa o venv manualmente no PowerShell:

  PowerShell:
  ```powershell
  .\venv\Scripts\Activate.ps1
  # depois rode pip install... normalmente
  ```

  Prompt (cmd):
  ```bat
  call venv\Scripts\activate.bat
  ```

Verificações rápidas:
- Depois de ativar o venv, verifique as variáveis:
  ```powershell
  echo $env:PIP_CACHE_DIR  # PowerShell
  echo %PIP_CACHE_DIR%     # cmd
  echo $env:TEMP           # PowerShell
  ```

- Você também pode checar onde o pip está usando cache:
  ```powershell
  python -m pip cache dir
  ```

Notas:
- Alguns instaladores/binaries podem ainda criar arquivos temporários em locais controlados pelo próprio instalador; definir `TMP`/`TEMP` minimiza esse risco pois muitos utilitários respeitam essas variáveis.
- Essas alterações só afetam o ambiente ativado (ou o `start-server.bat`); não alteram o cache global do usuário.
