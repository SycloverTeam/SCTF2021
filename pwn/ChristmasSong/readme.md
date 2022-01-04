# Christmas Song

[toc]

## 题目描述

一个真正的黑客可以在短时间内学习一个新语言的简单用法， 你可以在一天内学会圣诞歌么？注意播放圣诞歌不能说话！(flag范围dic = string.ascii_letters + string.digits + "*}")(slang 圣诞特别版 请检查源码包 https://drive.google.com/file/d/1uKjp2MGWdLWcwx4wfnpsMNEzXacb0ZbO/view?usp=sharing )
A real hacker can learn the simple usage of a new language in a short time, can you learn Christmas songs in a day? Note that you can’t talk when playing Christmas songs! (flag range dic = string.ascii_letters + string.digits + "*}) (slang Christmas Special Edition Please check the source code package https://drive.google.com/file/d/1uKjp2MGWdLWcwx4wfnpsMNEzXacb0ZbO/view?usp=sharing )

题目分值：625

解题人数：13

题目源码：[slang -christmas](https://github.com/wlingze/Slang/tree/christmas)， 

## Slang-christmas设计思路 1

### 设计

语言源码为`*.slang`文件，编译后的opcode文件为`*.scom`文件，

提供编译，运行， 反汇编三种操作。

```c
void help(){
    puts("Slang v0.01");
    puts("compile file:\t\t-c [filename.slang]");
    puts("decompile file:\t\t-d [filename.scom]");
    puts("run file\t\t-r [filename.scom/filename.slang]");
}

int main(int argc, char * argv[]){
    if (argc == 1){
        help();
    }

    for(int i=1; i<argc; i+=2){
        char * sig = argv[i];
        if (sig == NULL){
            return 1;
        }
        if (!strcmp(sig, "-c")){
            FLAG = COMPILE;
        } else if (!strcmp(sig, "-g")){
            FLAG = DEBUG;
        } else if (!strcmp(sig, "-d")){
            FLAG = DISASM;
        } else if (!strcmp(sig, "-r")){
            FLAG = RUN;
        } else {
            help();
            return 0;
        }
        load_file(argv[i+1]);
    }
    return 0;
}
```

```c

void load_file(char *path){
    char dir[0x60];
    char name[0x60];
    char slang_file[0x120];
    char scom_file[0x120];

    int is_slang = check_suffix(path, dir, name);

    snprintf(slang_file, 0x120, "%s/%s.slang", dir, name);
    snprintf(scom_file, 0x120, "%s/%s.scom", dir, name);

    if (FLAG == COMPILE){
        if (is_slang)
            compile_file(slang_file, scom_file);
        printf("compile file scom\n");
    } else {
        if (is_slang)
            compile_file(slang_file, scom_file);
        lambda_t *lambda = load_scom(scom_file);

        if (FLAG == RUN)
            vm_call_lambda(lambda);
        if (FLAG == DISASM)
            disasm(lambda);
    }
}
```

### 目录结构

com目录下是语法描述文件`parser.y`和词法描述文件`scanner.l`， 其他的是ast相关结构和生成opcode相关的代码，

dsiasm目录下是反汇编相关代码，

file目录是scom文件和载入文件的代码。

include 目录下是对应外面几个目录的头文件目录。

lib目录下是全局会使用到的相关结构。

vm目录下是运行的虚拟机。

![image.png](https://s2.loli.net/2022/01/03/bjExJ3SCmyi6RLT.png)



### 语法

一共支持三种结构，函数调用、want结构、赋值运算。

![image.png](https://s2.loli.net/2022/01/03/SKzHjEFga394Y6v.png)

其中want结构语法如下，相关代码在`com/com_want.c`中，是个类似switch的结构，可以构造出if语句，`AGAIN`可以重新跳回起点，于是也可以构造循环语句。

![image.png](https://s2.loli.net/2022/01/03/DH7k4vNc8wfFEiW.png)

函数调用语句如下，三种格式，通过BACK可以获取返回值。在`com/compile.c: compile_function`函数中是对应的代码。

![image.png](https://s2.loli.net/2022/01/03/9Va1edTZYozKvAk.png)

最后赋值语句，是可以进行计算的。

![image.png](https://s2.loli.net/2022/01/03/dojhwHRX5ClUiEs.png)

### 运行

在`vm/vm_call.c`中就是vm部分，比较典型的while+switch形式，相关运算赋值指令基于栈实现。

```c
#define display(OPCODE, opcode)                                                \
  case OP_##OPCODE:                                                            \
    vm_opcode_##opcode(r, l);                                                  \
    break
#define operator(OPCODE)                                                \
  case OP_##OPCODE:                                                     \
    vm_opcode_operator(r, l, OP_##OPCODE);                              \
    break
void vm_call_lambda(lambda_t *l){
    runtime_t *r = runtime_init();

    // gift to Christmas Bash!
    // Don't play too late for the party! Remember to sleep!

    // gift_t * gift = gift_init("sleep", sleep);
    // runtime_set_gift(r, gift);

    while(r->is_run){
        switch(get_code){
            display(STORE, store);
            display(LOAD_NUMBER, load_number);
            display(LOAD_STRING, load_string);
            display(LOAD_WORD, load_word);

            display(CALL, call);
            display(JZ, jz);
            display(JMP, jmp);

            operator(ADD);
            operator(SUB);
            operator(DIV);
            operator(MUL);
            operator(GRAETER);
            operator(EQUAL);
        }
        check_next(r, l);
    }
}
```

函数调用对应的代码如下，在Song题目中，不允许使用write， 

可以看到能使用的函数为` read` `open` `strncmp` `memcpy`， 对应名称 `Dasher ` `Dancer` `Prancer` `Vixen`

> 这其实是圣诞老人的九只驯鹿。

```c
char * rudolph = "Rudolph has been with Santa. \nGoing to deliver presents soon!\nYou can't get him to help. \nAnd you can't talk when playing Christmas songs!\n";

#define is_func(func_name) \
    !strcmp(func, (func_name))
void vm_opcode_call(arg){
    char *func = get_word;
    u_int64_t arg3 = pop;
    u_int64_t arg2 = pop;
    u_int64_t arg1 = pop;
    u_int64_t ret;

    if (is_func("Rudolph")){
        // ret = write(arg1, arg2, arg3);
        // No talking while singing Christmas Songs
        printf("error: \n%s\n", rudolph);
    }
    if (is_func("Dasher")){
        ret = read(arg1, arg2, arg3);
    }
    if (is_func("Dancer")){
        ret = open(arg1, arg2, arg3);
        if((int)ret < 0){
            printf("error con't open file %s\n", arg1);
            exit(EXIT_FAILURE);
        }
    }
    if (is_func("Prancer")){
        ret = strncmp(arg1, arg2, arg3);
    }
    if (is_func("Vixen")){
        ret = memcpy(arg1, arg2, arg3);
    }
    push(ret);
}
#undef is_func
```

## docker

题目使用`server.py`启动，主要位置在这里

```python
def run_challenge(filename):
    socket_print("Testing edge compute app...")
    try: 
        result = subprocess.run("/home/ctf/Christmas_Song -r {}.slang".format(filename), shell=True, timeout=1)
    except subprocess.TimeoutExpired:
        pass
    clean(filename);
    socket_print("Test complete!")
```

可以看到有个timeout=1，

## 思路

简单了解这个语言应该就可以做题了，这个song题目无关漏洞，

我们可以直接使用 `open` `read` 然后配合 `strncmp`和want结构形成的while语句实现一个死循环爆破，因为设置了超时时间，这个爆破速度也比较可观。

另一个思路是通过open失败的打印，这里直接再次open(flag)，失败后会进行打印，可以吧flag打印出来。

```c
    if (is_func("Dancer")){
        ret = open(arg1, arg2, arg3);
        if((int)ret < 0){
            printf("error con't open file %s\n", arg1);
            exit(EXIT_FAILURE);
        }
    }
```

