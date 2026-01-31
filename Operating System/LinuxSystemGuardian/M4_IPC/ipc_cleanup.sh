#!/bin/bash
# Script to remove the Message Queue

KEY=1234 # Must match MSG_KEY in ipc_common.h

echo "--- IPC Resource Cleanup ---"
# Use ipcs to find the queue ID, then ipcrm to remove it.
# You can also directly use the key with 'ipcrm -Q $KEY'
ipcrm -Q $KEY 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Message Queue (Key: $KEY) successfully removed."
else
    echo "Message Queue (Key: $KEY) not found or removal failed."
fi