#!/bin/bash

# Define the directory where the script is located
BASE_DIR=$(dirname "$0")

# --- 1. SETUP AND COMPILATION ---
echo "--- Preparing System Guardian Modules ---"
chmod +x "$BASE_DIR/M1_SystemSnapshot/system_snapshot.sh"
chmod +x "$BASE_DIR/M2_ProcessManager/child_task.sh"
chmod +x "$BASE_DIR/M4_IPC/ipc_cleanup.sh"
mkdir -p "$BASE_DIR/logs"

# Compile all modules
g++ "$BASE_DIR/M2_ProcessManager/process_manager.cpp" -o "$BASE_DIR/M2_ProcessManager/manager_exe"
g++ "$BASE_DIR/M3_FileAnalyzer/multithreaded_analyzer.cpp" -o "$BASE_DIR/M3_FileAnalyzer/analyzer_exe" -pthread
gcc "$BASE_DIR/M4_IPC/ipc_sender.c" -o "$BASE_DIR/M4_IPC/sender_exe"
gcc "$BASE_DIR/M4_IPC/ipc_receiver.c" -o "$BASE_DIR/M4_IPC/receiver_exe"

show_menu() {
    
    echo "==================================================="
    echo "       LINUX SYSTEM GUARDIAN - MASTER MENU"
    echo "==================================================="
    echo "1) Module 1: System Snapshot (Bash/Monitoring)"
    echo "2) Module 2: Process Manager (C++/Fork/Exec)"
    echo "3) Module 3: File Analyzer (C++/Pthreads/Mutex)"
    echo "4) Module 4: IPC (C/Message Queues)"
    echo "5) Run All Modules (Full Demonstration)"
    echo "6) Exit"
    echo "==================================================="
}

print_header() {
    echo ""
    echo "***************************************************"
    echo " STARTED: $1 "
    echo "***************************************************"
    echo ""
}


print_footer() {
    echo ""
    echo "***************************************************"
    echo " COMPLETED: $1 "
    echo "***************************************************"
    echo ""
}

run_module_1() {
    print_header "MODULE 1 - SYSTEM SNAPSHOT"
    "$BASE_DIR/M1_SystemSnapshot/system_snapshot.sh"
    print_footer "MODULE 1"
}

run_module_2() {
    print_header "MODULE 2 - PROCESS MANAGER"
    "$BASE_DIR/M2_ProcessManager/manager_exe"
    print_footer "MODULE 2"
}

run_module_3() {
    print_header "MODULE 3 - MULTITHREADED ANALYZER"
    "$BASE_DIR/M3_FileAnalyzer/analyzer_exe" "$BASE_DIR/M3_FileAnalyzer/sample_text.txt"
    print_footer "MODULE 3"
}

run_module_4() {
    print_header "MODULE 4 - IPC DEMONSTRATION"
    echo "[Sender] Sending messages to the kernel queue..."
    "$BASE_DIR/M4_IPC/sender_exe"
    echo ""
    echo "[Receiver] Retrieving messages from the kernel queue..."
    "$BASE_DIR/M4_IPC/receiver_exe"
    echo ""
    "$BASE_DIR/M4_IPC/ipc_cleanup.sh"
    print_footer "MODULE 4"
}

while true; do
    show_menu
    read -p "Select an option [1-6]: " choice
    case "$choice" in
        1)
            run_module_1
            ;;
        2)
            run_module_2
            ;;
        3)
            run_module_3
            ;;
        4)
            run_module_4
            ;;
        5)
            print_header "RUN ALL MODULES"
            run_module_1
            run_module_2
            run_module_3
            run_module_4
            print_footer "RUN ALL MODULES"
            ;;
        6)
            echo "Exiting System Guardian. Goodbye!"
            break
            ;;
        *)
            echo "Invalid option. Please choose 1-6."
            sleep 1
            ;;
    esac
done