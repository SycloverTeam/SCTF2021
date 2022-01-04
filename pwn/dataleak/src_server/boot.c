//
// Created by wlz on 9/14/21.
//
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>
#include <string.h>

int main() {
    setvbuf(stdin, 0LL, 2, 0LL);
    setvbuf(stdout, 0LL, 2, 0LL);
    setvbuf(stderr, 0LL, 2, 0LL);

    unsigned char magic[] = "sctf2021";
    unsigned char a[2];
    char buf[23] = {0};
    FILE * fptr;

    // time-rand => key
    srand((unsigned int)time(NULL));
    a[0] = rand() % 0xff;
    a[1] = rand() % 0xff;

    // key - magic => m
    for (int i=0; i<4; i++){
        magic[2*i] = magic[2*i] ^ a[0];
        magic[2*i + 1] = magic[2*i + 1] ^ a[0];
    }

    // m => string
    sprintf(buf, "%02x", magic[0]);
    for (int i=1; i<8; i++)
        sprintf(buf, "%s%02x", buf, magic[i]);
    sprintf(buf, "%s00", buf);
    sprintf(buf, "%s%02x", buf, a[0]);
    sprintf(buf, "%s%02x", buf, a[1]);

    printf("Please enter json and try to leak the data, which is generated randomly each time and has a length of 22.\n");

    int pid = fork();
    if (pid){
        // wait
        int status;
        waitpid(pid, &status, 0);
    } else {
        // pwn
        char *argv[]={"cJSON_PWN", buf, NULL};
        char *envp[]={0, NULL};
        execve("cJSON_PWN", argv, envp);
    }

    // check
    printf("\n");
    char input[23] = {0};
    printf("input your leaked data:\n");
    scanf("%22s", input);
    if (!strncmp(input, buf, 22))
        printf("SCTF{cJSON_1eakdata_Never_trust_4n_escape_character}\n");
    return 0;
}


