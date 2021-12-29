<?php
define('SERVER_PATH', __DIR__);

if (!is_dir(SERVER_PATH."/sandbox/")) {
    @mkdir(SERVER_PATH."/sandbox/");
}

$key = sha1($_SERVER['REMOTE_ADDR']);
$sandbox = SERVER_PATH."/sandbox/".$key."/";
$sandbox_html_path = "/sandbox/".$key."/";
$sandbox_dir = [
    "index" => $sandbox."/index.php",
    "class" => $sandbox."/class.php",
    "code" => $sandbox."/class.code",
    "lock" => $sandbox."/.lock"
];

function generate_new_code() {
    global $sandbox;
    global $sandbox_dir;

    exec("python3 /app/code/main.py \"$sandbox\"");
    copy($sandbox_dir["class"], $sandbox_dir["code"]);
    $index_data = <<<CODE
<?php
include "class.php";
@unserialize(\$_GET["data"]);
highlight_file(__FILE__);

/*
* You can get the TREE for the "./class.php" in the "./class.code".
* You can reset the "./class.php" after half an hour.
* Enjoy Your TREE :D
*/
CODE;
    file_put_contents($sandbox_dir["index"], $index_data);
    file_put_contents($sandbox_dir["lock"], time());
}

if (!is_dir($sandbox)) {
    @mkdir($sandbox);
}

if (!empty($_GET["get_code"])) {
    if (file_exists($sandbox_dir["lock"])) {
        $set_time = intval(file_get_contents($sandbox_dir["lock"]), 10);
        $through_time = time() - $set_time;
        if ($through_time > 60 * 30) {
            generate_new_code();
            $msg = "Tree generation successful, visit: <a href='$sandbox_html_path'>".$sandbox_html_path."</a>";
        } else {
            $wait_time = 60 * 30 - $through_time;
            $msg = "You’re gonna have to wait $wait_time seconds. visit: <a href='$sandbox_html_path'>".$sandbox_html_path."</a>";
        }
    } else {
        generate_new_code();
        $msg = "Tree generation successful, visit: <a href='$sandbox_html_path'>".$sandbox_html_path."</a>";
    }
} else {
    $msg = "Can you find your fumo on the Christmas tree?";
}

include "static/index.php";