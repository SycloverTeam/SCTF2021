# Dataleak 

[toc]

## 题目描述

Never trust c pointer magic and escape characters,

题目分值：281

解题人数：52

## 出题思路

最开始其实是cjson这个组件的漏洞 ，主要是 [CVE-2019-11834](https://github.com/DaveGamble/cJSON/issues/337)和[CVE-2019-11835](https://github.com/DaveGamble/cJSON/issues/338)，

两个cve都可以 实现跳过两个字节的功能，于是设计了这么一个数据泄露的题目 ，

## 漏洞位置

处理`/*`的时候会跳过两个字符， 

![image-20220102222216640](https://s2.loli.net/2022/01/02/e6srBoGQUD3bYuV.png)

处理`"`的时候如果有`\`会跳过两个字符，

![image-20220102222233867](https://s2.loli.net/2022/01/02/VLIBKDjrwqmAC6G.png)

## 内存布局

![image-20220102222509844](https://s2.loli.net/2022/01/02/8GBscmvkDXnhRxF.png)

两个buf长度为0x10, 写入数据为14, 在结尾有两个00, 数据在后面，每次从buf1开始处理，然后打印buf2中的11字节，数据一共22字节，在两次内打印出来，



![image-20220102224502177](https://s2.loli.net/2022/01/02/xN6TqbmXndYoksv.png)

于是我们的思路是，通过跳过两字节从buf1到buf2， 然后再从buf2跳到data， 

但是要注意， `"`的方案将会将数据保留，`\*`的方案将会将数据舍去， 于是可以将data写入到buf2的位置，控制前面的占位， 即可在两次打印中打印出来完整的data， 

## 远程

原设计是直接泄漏flag出来，后面想到泄漏flag且flag固定，可能存在多次泄漏出来的情况，

于是增加了一层loader， 

```c
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
```

## exp

这个exp极为简单，

payload : `"aaaaaaaaaaaa\/*aaaaaaaaaaaa/*aaaaaaaaaaaaaaaaa/*aaaaaaa`

