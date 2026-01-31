#!/bin/bash

# Define the directory where the executables and scripts are located
BASE_DIR=$(dirname "$0")

echo "==================================================="
echo "=== Linux System Guardian: Full Project Execution ==="
echo "==================================================="

# --- 0. PREP: Ensure all scripts are executable ---
echo "--- 0. Setting permissions for scripts ---"
chmod +x "$BASE_DIR/M1_SystemSnapshot/system_snapshot.sh"
chmod +x "$BASE_DIR/M2_ProcessManager/child_task.sh"
chmod +x "$BASE_DIR/M4_IPC/ipc_cleanup.sh"
echo "Permissions set."
sleep 1

# --- 1. SETUP AND COMPILATION ---
# ... (Compilation block remains the same)

echo "--- 1. Compiling C/C++ Modules ---"
# Compile Module 2 (Make sure process_manager.cpp is updated with the correct path!)
echo "Compiling Module 2 (Process Manager)..."
g++ "$BASE_DIR/M2_ProcessManager/process_manager.cpp" -o "$BASE_DIR/M2_ProcessManager/manager_exe"
if [ $? -ne 0 ]; then echo "Error compiling M2. Aborting."; exit 1; fi

# Compile Module 3
echo "Compiling Module 3 (Multithreaded File Analyzer)..."
g++ "$BASE_DIR/M3_FileAnalyzer/multithreaded_analyzer.cpp" -o "$BASE_DIR/M3_FileAnalyzer/analyzer_exe" -pthread
if [ $? -ne 0 ]; then echo "Error compiling M3. Aborting."; exit 1; fi

# Compile Module 4
echo "Compiling Module 4 (IPC Sender/Receiver)..."
gcc "$BASE_DIR/M4_IPC/ipc_sender.c" -o "$BASE_DIR/M4_IPC/sender_exe"
gcc "$BASE_DIR/M4_IPC/ipc_receiver.c" -o "$BASE_DIR/M4_IPC/receiver_exe"
if [ $? -ne 0 ]; then echo "Error compiling M4. Aborting."; exit 1; fi

echo "Compilation successful."
sleep 1

# --- 2. EXECUTE MODULE 1: System Snapshot (Bash) ---
# ... (Execution block for M1 remains the same)
echo ""
echo "==================== M O D U L E   1 ===================="
echo "Demonstrates: Shell Scripting, System Monitoring"
"$BASE_DIR/M1_SystemSnapshot/system_snapshot.sh"
echo "--- M1 Complete ---"
sleep 2


# --- 3. EXECUTE MODULE 2: Process Manager (C++/fork) ---
# ... (Execution block for M2 remains the same)
echo ""
echo "==================== M O D U L E   2 ===================="
echo "Demonstrates: Process Creation, Synchronization, Program Replacement"
"$BASE_DIR/M2_ProcessManager/manager_exe"
echo "--- M2 Complete ---"
sleep 2

# --- 4. EXECUTE MODULE 3: Multithreaded Analyzer (C++/pthreads) ---
# ... (Execution block for M3 remains the same)
echo ""
echo "==================== M O D U L E   3 ===================="
echo "Demonstrates: Multithreading, Concurrency, Mutex Locks"
"$BASE_DIR/M3_FileAnalyzer/analyzer_exe" "$BASE_DIR/M3_FileAnalyzer/sample_text.txt"
echo "--- M3 Complete ---"
sleep 2

# --- 5. EXECUTE MODULE 4: IPC Message Queue (C/System V) ---
# ... (Execution block for M4 remains the same)
echo ""
echo "==================== M O D U L E   4 ===================="
echo "Demonstrates: Inter-Process Communication (IPC), Message Queues"
echo "Running Sender (P1) -> Placing messages on queue..."
"$BASE_DIR/M4_IPC/sender_exe"
echo ""
echo "Running Receiver (P2) -> Reading messages from queue..."
"$BASE_DIR/M4_IPC/receiver_exe"
echo "--- M4 Complete ---"
sleep 2

# --- 6. CLEANUP ---
# ... (Cleanup block remains the same)
echo ""
echo "====================== C L E A N U P ======================"
"$BASE_DIR/M4_IPC/ipc_cleanup.sh"
echo "Cleanup finished."

echo "==================================================="
echo "=== All Modules Executed Successfully. Check logs/ folder for output. ==="
echo "==================================================="