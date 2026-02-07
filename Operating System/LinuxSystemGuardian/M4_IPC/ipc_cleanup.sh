#!/bin/bash

KEY=1234

echo "--- IPC Resource Cleanup ---"
ipcrm -Q $KEY 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Message Queue (Key: $KEY) successfully removed."
else
    echo "Message Queue (Key: $KEY) not found or removal failed."
fi