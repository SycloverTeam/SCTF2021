# gadget 

* [gadget](#gadget)
   * [题目描述](#题目描述)
   * [编译环境](#编译环境)
   * [ora思路](#ora思路)
   * [gadget](#gadget-1)
      * [出题考点](#出题考点)
      * [栈迁移](#栈迁移)
      * [mov rdx](#mov-rdx)
      * [alarm](#alarm)

## 题目描述

总要有人整治下套路化的gadget吧 (远程环境可以先查看./test文件内容为\x01\x02\x03\x04\x05\x06检测自己exp是否正确)

分值： 487

解题人数： 22



## 编译环境

出题思路其实来自[这个题目]()，非常规的gadget拼凑，

这个题目的编译环境是ollvm编译出的musl libc， 然后使用这个musl去静态编译出文件来。从而得到的文件中的gadget就很少见了。

![image-20211112202707893](https://s2.loli.net/2022/01/02/m4PVCEkhUFo3jOd.png)

## ora思路

![image-20211112202551950](https://s2.loli.net/2022/01/02/RpgawNKQUcSYTs6.png)

看到沙盒应该就有对应的思路了，先使用retfq跳到32位使用open， 然后回到64位使用read， 最后通过alarm得到flag， 

这应该是shellcode题目常见的思路，

## gadget

这里相关的gadget都通过内联汇编或者赋值语句放在程序内了，用ropper查找应该会比ROPgadget效果好一些些。

```c
    // pop rcx; retn;
    int ret = 0xc359;

    // jmp $ 
    int b = 0xfeeb;

    // retfq
    int a = 0xcb48;
    // int 80; retn;
    int b = 0xc380cd;

    asm volatile(
        "movb (%rsi, %rax), %bl\n\t"
        "mov %rbx, %rdi\n\t"
        "push %r14\n\t"
        "ret\n\t"
     );
```

### 出题考点

其实个人对于gadget的理解是这样的： 

一小段代码，它的结构大概是如此: `[功能][副作用][再次控制]`， 

这个功能是我们想要让他运行的代码。

副作用即 我们运行这个gadget必定会向下运行，必须要让他满足的一些指令，或者会干扰我们利用的一些操作也要去处理掉。

再次控制可以是ret， 或者call/jmp某个寄存器，都是ok的，

### 栈迁移

原本思路是通过leave栈迁移，

> 其实这个第一条完全可用，而且比第一条还短。🧐

![image-20211112204517189](https://s2.loli.net/2022/01/02/VAOEFwbgzYXvopI.png)

那么这里有一个长度限制，使用`pop rdi, jmp rax;`会比`pop rdi; pop rap; ret`少一个字节，

![image-20211112203428200](https://s2.loli.net/2022/01/02/aK1pwkNObcFLfsM.png)

并且在main函数返回的时候已经设置好了这个rax的值

![image-20211112203553814](https://s2.loli.net/2022/01/02/wHzkxYv2j3fnL5p.png)

看到很多师傅通过pop rsp进行栈迁移了，这个在出题的时候确实没有考虑到，这个方案可以更简单一些。

### mov rdx

在gadget中其实是没有可用的`pop rdx`相关的，

![image-20211112204006171](https://s2.loli.net/2022/01/02/pu7C4XxWrbVJE8g.png)

> 这个最后的 `ret 0xfdbf;`会让栈降低 0xfdbf个大小，不可控

但是有个这样的gadget路线

![image-20211112204105740](https://s2.loli.net/2022/01/02/JtPZqQO8ilGkEMj.png)

注意这个 `mov rdx, r12; call r14;`， 

![image-20211112204114078](https://s2.loli.net/2022/01/02/Oy6nKwGFizVC7R4.png)

这两个寄存器我们都可以控制，于是可以借助这个控制rdx， 

同时，由于是`call r14`， 会有返回地址压栈， 于是我们将r14设置到一个随意一个`pop ;ret`的结构即可。



但是出题仍然没处理好这个位置，主要一开始对于ollvm不太熟，会把这个位置混淆了，于是就吧参数全设置到read内了，后来用了`__attribute`但是忘了改回来，这样就提供了可以直接跳过来不控制rdx的方案，

![image-20211112210115902](https://s2.loli.net/2022/01/02/YPoigtFuK8mRfAs.png)

而且一直到放题目也没有再注意到这个点，所以这个位置其实出简单了 qaq

### alarm 

其实这个位置预期就是ora嘛，使用alarm即可，这里给了个gadget用来取出flag每一位，

![image-20211112210737186](https://s2.loli.net/2022/01/02/skQcNqREtIgf6vi.png)

但是要注意的是，这里是bl, 下面传递是rbx, 需要提前清理掉rbx中的数据，不然还是g， 

