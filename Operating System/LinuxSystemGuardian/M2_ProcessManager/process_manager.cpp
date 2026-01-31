#include <iostream>
#include <fstream>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>

using namespace std;

// Function to log process info (similar to the log file mentioned in Module 1) [cite: 41]
void log_process(const string& message) {
    ofstream log_file("logs/M2_process_log.txt", ios::app);
    if (log_file.is_open()) {
        log_file << message << endl;
        log_file.close();
    }
}

int main() {
    cout << "--- Linux System Guardian: Process Manager Mini-Simulator ---" << endl;
    log_process("\n--- New Simulation Start ---");
    
    pid_t pid;
    int num_children = 3;

    for (int i = 0; i < num_children; ++i) {
        pid = fork(); // Create a new child process [cite: 37]

        if (pid < 0) {
            // Fork failed
            cerr << "Fork failed for child " << i + 1 << endl;
            log_process("Fork failed");
            return 1;
        } else if (pid == 0) {
            // Child process executes this block
            
            cout << "Child " << i + 1 << " created. PID: " << getpid() << ", Parent PID: " << getppid() << endl;
            
            // Program replacement: Child runs the external task script [cite: 38]
            char *args[] = {(char*)"M2_ProcessManager/child_task.sh", (char*)0};
            // The path must be relative to the executable's location
            execv(args[0], args); 
            
            // If execv returns, it must have failed
            cerr << "Exec failed for child " << i + 1 << endl;
            exit(1);

        } else {
            // Parent process executes this block
            string log_msg = "Parent (PID: " + to_string(getpid()) + ") created Child (PID: " + to_string(pid) + ")";
            log_process(log_msg);
        }
    }

    // --- Process Synchronization ---
    cout << "\nParent is waiting for all " << num_children << " children to finish..." << endl;

    int status;
    pid_t wpid;

    // Parent waits for all children to exit [cite: 39]
    while ((wpid = wait(&status)) > 0) {
        cout << "Child (PID: " << wpid << ") finished." << endl;
        
        // Check if the child exited normally
        if (WIFEXITED(status)) {
            int exit_status = WEXITSTATUS(status);
            cout << "  - Exit Status: " << exit_status << endl; // Prints exit status [cite: 40]
            string log_msg = "Child (PID: " + to_string(wpid) + ") exited with status: " + to_string(exit_status);
            log_process(log_msg);
        } else {
            cout << "  - Child terminated abnormally." << endl;
            log_process("Child (PID: " + to_string(wpid) + ") terminated abnormally.");
        }
    }

    cout << "\nParent (PID: " << getpid() << ") finished managing all processes." << endl;
    cout << "Module 2 demonstration complete. Check M2_process_log.txt." << endl;
    return 0;
}