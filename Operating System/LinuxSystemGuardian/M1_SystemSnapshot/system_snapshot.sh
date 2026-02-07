#!/bin/bash

LOG_DIR="./logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/system-log-$TIMESTAMP.txt"

mkdir -p "$LOG_DIR"

echo "--- Linux System Guardian: System Snapshot ---"
echo "Log file: $LOG_FILE"
echo ""

UPTIME=$(uptime -p)
echo "1. System Uptime: $UPTIME"
echo "----------------------------------------" >> "$LOG_FILE"
echo "Timestamp: $(date)" >> "$LOG_FILE"
echo "System Uptime: $UPTIME" >> "$LOG_FILE"

CPU_LOAD=$(awk '{print $1, $2, $3}' /proc/loadavg)
echo "2. CPU Load (1m, 5m, 15m): $CPU_LOAD"
echo "CPU Load (1m, 5m, 15m): $CPU_LOAD" >> "$LOG_FILE"

echo "3. RAM Usage (MB):"
RAM_INFO=$(free -m | awk 'NR==2{printf "  Total: %s MB\n  Used: %s MB\n  Free: %s MB", $2, $3, $4}')
echo -e "$RAM_INFO"
echo "RAM Usage (MB):" >> "$LOG_FILE"
echo -e "$RAM_INFO" >> "$LOG_FILE"


echo "4. Disk Usage (/):"
DISK_USAGE=$(df -h / | awk 'NR==2{printf "  Size: %s\n  Used: %s\n  Available: %s\n  Use Percent: %s", $2, $3, $4, $5}')
echo -e "$DISK_USAGE"
echo "Disk Usage (/):" >> "$LOG_FILE"
echo -e "$DISK_USAGE" >> "$LOG_FILE"

PROCESS_COUNT=$(ps -e | wc -l)
PROCESS_COUNT=$((PROCESS_COUNT - 1))
echo "5. Running Processes Count: $PROCESS_COUNT"
echo "Running Processes Count: $PROCESS_COUNT" >> "$LOG_FILE"


echo "----------------------------------------"
echo "Successfully generated log: $LOG_FILE"
echo "Module 1 demonstration complete."