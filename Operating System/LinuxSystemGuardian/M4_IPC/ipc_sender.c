#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include "ipc_common.h"

int main() {
    int msqid;
    struct message_buf sbuf;
    size_t buf_length;

    printf("--- Module 4: IPC Sender (Process 1) ---\n");

    msqid = msgget(MSG_KEY, IPC_CREAT | 0666);
    if (msqid < 0) {
        perror("msgget failed");
        exit(1);
    }
    printf("Message Queue ID (msqid) obtained: %d\n", msqid);

    sbuf.mtype = NOTIFICATION_TYPE;
    strcpy(sbuf.mtext, "System Alert: Disk space is getting low (Type 1).");
    buf_length = strlen(sbuf.mtext) + 1;
    if (msgsnd(msqid, &sbuf, buf_length, 0) < 0) {
        perror("msgsnd failed for notification 1");
        exit(1);
    }
    printf("Sent [Type %ld] message: '%s'\n", sbuf.mtype, sbuf.mtext);


    sbuf.mtype = EMERGENCY_TYPE;
    strcpy(sbuf.mtext, "CRITICAL: System integrity compromised. Immediate attention required (Type 2)!");
    buf_length = strlen(sbuf.mtext) + 1;
    if (msgsnd(msqid, &sbuf, buf_length, 0) < 0) {
        perror("msgsnd failed for notification 2");
        exit(1);
    }
    printf("Sent [Type %ld] message: '%s'\n", sbuf.mtype, sbuf.mtext);

    printf("Sender finished sending messages.\n");
    return 0;
}