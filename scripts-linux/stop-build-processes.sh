#!/bin/bash

################################################################################
# Stop Build and Python Processes
# Para forcadamente todos os processos de build/Python
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Parando Processos de Build/Python"
echo -e "========================================${NC}"
echo ""

# Array of processes to stop
processes_to_stop=("python3" "python" "pip3" "pip" "gcc" "g++" "cc" "c++")

for proc_name in "${processes_to_stop[@]}"; do
    # Find all processes matching the name
    pids=$(pgrep -f "$proc_name" 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        for pid in $pids; do
            # Get process name and command
            proc_cmd=$(ps -p "$pid" -o cmd= 2>/dev/null)
            
            echo -e "${YELLOW}[*] Parando $proc_name (PID: $pid): $proc_cmd${NC}"
            
            if kill -9 "$pid" 2>/dev/null; then
                echo -e "${GREEN}[✓] Parado com sucesso${NC}"
            else
                echo -e "${RED}[!] Falha ao parar${NC}"
            fi
        done
    fi
done

echo ""
echo -e "${GREEN}[✓] Cleanup concluído${NC}"
echo ""
echo -e "${CYAN}Próximas ações:${NC}"
echo -e "  1. Feche o VS Code${NC}"
echo -e "  2. Reabra o VS Code${NC}"
echo -e "  3. Se persistir, reinicie o sistema${NC}"
echo ""
