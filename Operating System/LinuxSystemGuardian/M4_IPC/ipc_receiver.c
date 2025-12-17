#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <errno.h>
#include "ipc_common.h"

int main() {
    int msqid;
    struct message_buf rbuf;
    long msg_type_selector = 0; 

    printf("--- Module 4: IPC Receiver (Process 2) ---\n");

    msqid = msgget(MSG_KEY, 0666); 
    if (msqid < 0) {
        perror("msgget failed, ensure sender ran first");
        exit(1);
    }
    printf("Message Queue ID (msqid) obtained: %d\n", msqid);

    printf("\nAttempting to read the FIRST message (Type 0, Blocking)...\n");
    if (msgrcv(msqid, &rbuf, sizeof(rbuf.mtext), msg_type_selector, 0) < 0) {
        perror("msgrcv failed (blocking)");
        exit(1);
    }
    printf("RECEIVED [Type %ld, Blocking]: %s\n", rbuf.mtype, rbuf.mtext);

    
    msg_type_selector = EMERGENCY_TYPE;
    printf("\nAttempting to read a specific message (Type %ld, Non-Blocking)...\n", msg_type_selector);
    if (msgrcv(msqid, &rbuf, sizeof(rbuf.mtext), msg_type_selector, IPC_NOWAIT) < 0) {
        if (errno == ENOMSG) {
            printf("Non-Blocking Read: No message of Type %ld currently available.\n", msg_type_selector);
        } else {
            perror("msgrcv failed (non-blocking)");
            exit(1);
        }
    } else {
        printf("RECEIVED [Type %ld, Non-Blocking]: %s\n", rbuf.mtype, rbuf.mtext);
    }
    
    printf("\nReceiver finished.\n");
    return 0;
}