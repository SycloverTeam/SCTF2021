/*
     Created by wlz on 3/4/21.
*/

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../cJSON.h"


int main(int argc, char *argv[]) {

    setvbuf(stdin, 0LL, 2, 0LL);
    setvbuf(stdout, 0LL, 2, 0LL);
    setvbuf(stderr, 0LL, 2, 0LL);

    char buf1[16];
    char buf2[16];
    char leakdata[25];
    if (argc != 2){
        printf("argv error\n");
        exit(1);
    }
    char *data = argv[1];

    int i;

    for (i = 0; i < 2; i++) {
        memcpy(leakdata, data, 25);

        memset(buf1, 0, 16);
        memset(buf2, 0, 16);
        read(0, buf1, 14);
        read(0, buf2, 14);

        cJSON_Minify(buf1);

        write(1, buf2, 11);
    }
    return 0;
}
