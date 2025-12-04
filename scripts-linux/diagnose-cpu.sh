#!/bin/bash

################################################################################
# Diagnose CPU-Consuming Processes
# Diagnostica e mata processos que consomem alto CPU relacionados a build/Python
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Diagnóstico de Processos com Alto CPU"
echo -e "========================================${NC}"
echo ""

# Get top 10 processes by CPU usage
echo -e "${CYAN}[*] Top 10 processos por uso de CPU:${NC}"
echo ""

ps aux --sort=-%cpu | head -11 | awk '{printf "  PID: %6s | CPU: %5s%% | MEM: %5s%% | Command: %s\n", $2, $3, $4, $11}'

echo ""

# Look for known problematic processes
echo -e "${CYAN}[*] Procurando processos problemáticos...${NC}"
echo ""

suspects=("python3" "python" "pip3" "pip" "gcc" "g++" "make" "cc")
found_suspects=0

for proc_name in "${suspects[@]}"; do
    pids=$(pgrep -f "$proc_name" 2>/dev/null)
    
    if [ ! -z "$pids" ]; then
        for pid in $pids; do
            cpu_usage=$(ps -p "$pid" -o %cpu= 2>/dev/null)
            mem_usage=$(ps -p "$pid" -o %mem= 2>/dev/null)
            cmd=$(ps -p "$pid" -o cmd= 2>/dev/null)
            
            echo -e "${YELLOW}[!] Encontrado: $proc_name (PID: $pid, CPU: $cpu_usage%, RAM: $mem_usage%)${NC}"
            echo -e "    Command: $cmd"
            found_suspects=$((found_suspects + 1))
        done
    fi
done

if [ $found_suspects -eq 0 ]; then
    echo -e "${GREEN}[✓] Nenhum processo compilador/Python problemático encontrado${NC}"
else
    echo ""
    echo -e "${YELLOW}[*] Processos encontrados que podem estar causando o problema:${NC}"
    echo ""
    
    read -p "Deseja terminar estes processos? (s/n): " response
    if [ "$response" = "s" ] || [ "$response" = "S" ]; then
        for proc_name in "${suspects[@]}"; do
            pids=$(pgrep -f "$proc_name" 2>/dev/null)
            
            if [ ! -z "$pids" ]; then
                for pid in $pids; do
                    if kill -9 "$pid" 2>/dev/null; then
                        echo -e "${GREEN}[✓] Processo $proc_name (PID: $pid) terminado${NC}"
                    else
                        echo -e "${RED}[!] Falha ao terminar $proc_name (PID: $pid)${NC}"
                    fi
                done
            fi
        done
    fi
fi

echo ""
echo -e "${GREEN}========================================"
echo -e "Recomendações"
echo -e "========================================${NC}"
echo ""
echo -e "${CYAN}[i] Se o VS Code está lento/travado:${NC}"
echo -e "    1. Feche o VS Code completamente${NC}"
echo -e "    2. Execute: ${CYAN}./scripts-linux/stop-build-processes.sh${NC}"
echo -e "    3. Abra o VS Code novamente${NC}"
echo ""
echo -e "${CYAN}[i] Se um processo pip/compilador está travado:${NC}"
echo -e "    1. Execute este script e termine os processos${NC}"
echo -e "    2. Execute: ${CYAN}python3 xtts-server/start.py 4${NC}  (limpar e reinstalar)${NC}"
echo ""
echo -e "${CYAN}[i] Se o problema persistir:${NC}"
echo -e "    1. Reinicie o sistema${NC}"
echo -e "    2. Abra um novo terminal${NC}"
echo -e "    3. Execute: ${CYAN}python3 xtts-server/start.py install${NC}"
echo ""
