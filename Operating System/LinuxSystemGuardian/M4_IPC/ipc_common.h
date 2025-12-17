#ifndef IPC_COMMON_H
#define IPC_COMMON_H

#include <sys/types.h>

#define MSG_KEY 1234

struct message_buf {
    long mtype;
    char mtext[256];
};

#define NOTIFICATION_TYPE 1
#define EMERGENCY_TYPE 2

#endif