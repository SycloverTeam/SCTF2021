#include "types.h"
#include "param.h"
#include "memlayout.h"
#include "riscv.h"
#include "spinlock.h"
#include "proc.h"
#include "syscall.h"
#include "defs.h"

extern pte_t * walk(pagetable_t pagetable, uint64 va, int alloc);
uint64 sys_sycgame(void) {
    uint64 addrA;
    uint64 addrB;
    pte_t *pteA;
    pte_t *pteB;
    pte_t tmp;
    
    if(argaddr(0, &addrA) < 0)
        return -1;

    if(argaddr(1, &addrB) < 0)
        return -1;

    pteA = walk(myproc()->pagetable, addrA, 0);
    pteB = walk(myproc()->pagetable, addrB, 0);
    tmp = *pteA;
    *pteA = *pteB;
    *pteB = tmp;
    sfence_vma();
    return 1;
}