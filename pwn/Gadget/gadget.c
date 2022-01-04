//
// Created by wlz on 10/1/21.
//

#include <stdio.h>
#include <stdlib.h>
#include <sys/prctl.h> 

#define SECCOMP_MODE_FILTER 2

/* 

seccomp-tools asm sandbox.asm -f c_source

cat sandbox.asm:

A = sys_number
    A > 0x40000000 ? kill:next
    A == fstat ? allow:next
    A == read ? allow:next
    A == alarm ? allow:next
kill:
    return KILL
allow:
    return ALLOW

*/

static void install_seccomp() {
  static unsigned char filter[] = {32,0,0,0,0,0,0,0,37,0,3,0,0,0,0,64,21,0,3,0,5,0,0,0,21,0,2,0,0,0,0,0,21,0,1,0,37,0,0,0,6,0,0,0,0,0,0,0,6,0,0,0,0,0,255,127};
  struct prog {
    unsigned short len;
    unsigned char *filter;
  } rule = {
    .len = sizeof(filter) >> 3,
    .filter = filter
  };
  if(prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) < 0) { perror("prctl(PR_SET_NO_NEW_PRIVS)"); exit(2); }
  if(prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &rule) < 0) { perror("prctl(PR_SET_SECCOMP)"); exit(2); }
}

void alarm_sys(int s){
    asm volatile
    (
    "movl $37, %%eax\n\t"
    "movl %0, %%edi\n\t"
    "syscall"
    : : "g"(s)
    : "%rdi"
    );
}

int read_sys(void *buf) __attribute((__annotate__(("nofla"))));
int read_sys(void *buf) __attribute((__annotate__(("nobcf"))));
int read_sys(void *buf){

    // pop rcx; retn;
    int ret = 0xc359;
    asm volatile
    (
    "movl $0, %%eax\n\t"
    "movl $0, %%edi\n\t"
    "movq %1, %%rsi\n\t"
    "movl $200, %%edx\n\t"
    "syscall"
    : "=a"(ret)
    : "g"(buf)
    : "%rdi", "%rsi", "%rdx", "%rcx", "%r11"
    );
    return ret;
}

int func(int a) __attribute((__annotate__(("nofla"))));
int func(int a) __attribute((__annotate__(("nobcf"))));
int func(int a){

    // jmp $ 
    int b = 0xfeeb;

    asm volatile(
        "movb (%rsi, %rax), %bl\n\t"
        "mov %rbx, %rdi\n\t"
        "push %r14\n\t"
        "ret\n\t"
        );
    return 0;
}


int main() __attribute((__annotate__(("nofla"))));
int main() __attribute((__annotate__(("nobcf"))));
int main(){
    alarm_sys(0x30);
    char buf[0x20];

    // retfq
    int a = 0xcb48;
    // int 80; retn;
    int b = 0xc380cd;

    install_seccomp();
    read_sys(buf);

    asm volatile (
        "xor %rdx, %rdx\n\t"
        "mov $4, %rdi\n\t"
        "mov $4, %rsi\n\t"
        "mov $4198402, %rax\n\t"
        "add $64, %rsp\n\t"
        "pop %rbp\n\t"
        "ret\n\t"
    );
    return 0;
}