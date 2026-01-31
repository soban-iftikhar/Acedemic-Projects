#ifndef IPC_COMMON_H
#define IPC_COMMON_H

#include <sys/types.h>

// 1. Unique Key for the Message Queue
// This number (e.g., 1234) should be unique to the system/project
#define MSG_KEY 1234 
// ftok is often used to generate keys, but for simplicity here we use a fixed integer key.

// 2. Message Structure
// The message structure MUST start with a long integer type field.
struct message_buf {
    long mtype;     // Required message type field (must be > 0)
    char mtext[256]; // Message payload (the notification content)
};

// Message Type definitions
#define NOTIFICATION_TYPE 1
#define EMERGENCY_TYPE 2

#endif // IPC_COMMON_H