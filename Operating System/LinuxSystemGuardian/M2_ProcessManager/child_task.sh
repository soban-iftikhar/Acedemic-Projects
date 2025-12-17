#!/bin/bash

CHILD_PID=$$

echo "Child process (PID: $CHILD_PID) is running a quick task."
sleep 1
echo "Child process (PID: $CHILD_PID) finished successfully."

EXIT_STATUS=$((RANDOM % 6))
exit $EXIT_STATUS