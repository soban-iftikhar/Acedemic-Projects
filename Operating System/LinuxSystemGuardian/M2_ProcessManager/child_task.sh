#!/bin/bash
# Simple task for the child process to execute

# Get the PID from the environment (not strictly necessary but good for logging)
CHILD_PID=$$

echo "Child process (PID: $CHILD_PID) is running a quick task."
# Simulate a small amount of work or delay
sleep 1
echo "Child process (PID: $CHILD_PID) finished successfully."

# Exit with a random exit status between 0 and 5
# This demonstrates different exit statuses [cite: 40]
EXIT_STATUS=$((RANDOM % 6))
exit $EXIT_STATUS