import hashlib
import sys

def _rc4_crypt(key, data, dataLen):
    out = []
    s_box = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s_box[i] + ord(key[i % len(key)])) % 256
        s_box[i], s_box[j] = s_box[j], s_box[i]

    for x in range(dataLen):
        i = (i + 1) % 256
        j = (j + s_box[i]) % 256
        t = s_box[i]
        s_box[i] = s_box[j]
        s_box[j] = t
        ti = (s_box[i] + (s_box[j] % 256)) % 256
        t = s_box[ti]
        while (len(out) < x + 1):
            out.append(0)
        out[x] = data[x] ^ t
    return out

def linux_srand(seed):
    if seed == 0:
        seed = 1
    word = seed
    seed = seed & 0xffffffff
    global linux_status
    global linux_r
    linux_status = 0
    linux_r = [0] * (344 + linux_status)
    linux_r[0] = seed
    for i in range(1, 31):
        if (word < 0):
            hi = (-word) // 127773
            hi = -hi
            lo = (-word) % 127773
            lo = -lo
        else:
            hi = word // 127773
            lo = word % 127773
        word = ((16807 * lo)) - ((2836 * hi))
        if word < 0:
            word = (2147483647 + word) & 0xffffffff
        linux_r[i] = word
    for i in range(31, 34):
        linux_r[i] = linux_r[i - 31]
    for i in range(34, 344):
        linux_r[i] = (((linux_r[i - 31] + linux_r[i - 3]) & 0xffffffff) % (1 << 32)) & 0xffffffff

def linux_rand():
    global linux_status
    global linux_r
    linux_r.append(0)
    linux_r[344 + linux_status] = (((linux_r[344 + linux_status - 31] + linux_r[344 + linux_status - 3]) & 0xffffffff) % (1 << 32)) & 0xffffffff
    linux_status += 1
    return linux_r[344 + linux_status - 1] >> 1
print("hello challanger")
flag = input("please input your flag:\n")
if (type(flag) != str):
    print("error")
    sys.exit()
if (len(flag) != 17):
    sys.exit()
flag = list(bytes(flag, encoding='utf-8'))
flag = _rc4_crypt('Sycl0ver', flag, len(flag))
for i in range(len(flag)):
    linux_srand(flag[i])
    flag[i] = str(linux_rand())
ciphertext=['ee197bbac1b0e09c425e1dfd30cea2506bd493a674c4de90d9afbe5abc700b06',
'1a6aafb16a23ffde40c426d5c87f5afcc77fffc96cf041dc8dd2c47e706a7ecb',
'62c62ce7768a4836b10495317a32da6e3943d522bc3b9797ff0a44931e966a31',
'e6222354b50e4d33d73314b515b325633e57a105758e20aca23eb2dadd625f3f',
'78f92a6ad9ffcec47f30e3ca3d18065bdba9c020ff5f477b801d11efdfaa9cd0',
'127291de1f4cbbb35c41556a3c6d5a64f08661bc7ed394ea6210354e6218ad93',
'62c62ce7768a4836b10495317a32da6e3943d522bc3b9797ff0a44931e966a31',
'52080868c07a9ef5646b5f0b198f04f013cf23cfbfb06123d8f2fdd63d359123',
'f69b52599973fc5915ad1d435236863252dc3fd460989bd9f56ffc199ef8ff36',
'e9552f8c3e518306524fa9c9728ad6dee88fa611aa3068c169217f173964f9b4',
'54cb43f463ea082699131b71d45fb0384f8c2f598e8f0072b960b4add731e048',
'97e45e15c74f71ea59ffffb40298f2e5dec119c2205e434e3a0d2510c331037f',
'51b7d78cfe25ede262fd85a65b24721f076ab9dd6562403878ca5cde1ebf3219',
'a1cd6c7990abb6b271695381d78898ec5c4880fbc0f6a0c9fda064422f21361e',
'85ddd3721d173367465373f75e190bd937a8dc3588d5d82ebff8104dec88ac3e',
'd6eeac4ea40f9513391ef0bf72aa2fd2588889cb9d5f4cc638ce4d2c5509527b',
'5023939dca9273fd767d5e4ea329846f9816af461e170b6db8d20b6e5ff3de8c']
for i in range(len(flag)):
    for j in range(2560):
        s = hashlib.sha256()
        s.update(bytes(flag[i], encoding='utf-8'))
        flag[i] = s.hexdigest()
    #print("'" + flag[i]+ "',")
    if (flag[i] != ciphertext[i]):
        sys.exit()
print("you are right")
sys.exit()