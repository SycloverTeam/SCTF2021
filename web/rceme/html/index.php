<?php
if(isset($_POST['cmd'])){
	$code = $_POST['cmd'];
	if(preg_match('/[A-Za-z0-9]|\'|"|`|\ |,|-|\+|=|\/|\\|<|>|\$|\?|\^|&|\|/ixm',$code)){
		die('<script>alert(\'Try harder!\');history.back()</script>');
	}else if(';' === preg_replace('/[^\s\(\)]+?\((?R)?\)/', '', $code)){
        @eval($code);
		die();
	}
} else {
	highlight_file(__FILE__);
	var_dump(ini_get("disable_functions"));
}
?>
