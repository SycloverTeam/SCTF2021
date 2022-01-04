import json
import queue
from typing import Set

root_ast = json.load(open('res.json','rb'))
class_ast = root_ast[0]["stmts"]
classes_ast = {}
source = "source"

def get_funccall_name(expr):
    if expr['nodeType'] == "Expr_FuncCall":
        return expr['name']['parts'][0]
    print(expr)
    raise Exception("Not FunCall")

class Node:
    def __init__(self,parent:"Node",funcName:str,className:str,fromObj:str,operation:str="") -> None:
        self.parent:"Node" = parent
        self.funcname = funcName
        self.className = className
        self.children:Set[Node] = {}
        self.fromObj = fromObj
        self.operation = operation
    def __repr__(self) -> str:
        return f"Class:{self.className} Func:{self.funcname}"

def gen_decode_exp(encode_way):
    if encode_way == 'base64_decode':
        return 'base64_encode'
    elif encode_way == 'strrev':
        return 'strrev'
    elif encode_way == 'str_rot13':
        return 'str_rot13'
    elif encode_way == 'base64_encode':
        return 'base64_decode'
    elif encode_way == 'ucfirst':
        return 'lcfirst'
    else:
        print("Unkown Encode Way",encode_way)
        return ""

def printGraph(sink:Node)->bool:
    cur = sink
    decode_exp = '"/flag"'
    while True:
        print(f"{cur.className}::{cur.funcname} [{cur.operation}]<-",end='')
        cur = cur.parent
        if cur == None:
            break
        if cur.operation != "":
            decode_exp = f"{gen_decode_exp(cur.operation)}({decode_exp})"
    print('\n')
    print(decode_exp)

def printExp(cur:Node):
    ret = f"$my{cur.className} = new \christmasTree\{cur.className};\r\n"
    for stmt in classes_ast[cur.className]['stmts']:
            if stmt['nodeType'] == 'Stmt_Property':
                propName = stmt['props'][0]['name']['name']
                ret += f"$my{cur.className}->{propName} = new StdClass;\r\n"
    parent:Node = cur.parent
    while parent != None:
        tmp = f"$my{parent.className} = new \christmasTree\{parent.className};\r\n"
        for stmt in classes_ast[parent.className]['stmts']:
            if stmt['nodeType'] == 'Stmt_Property':
                propName = stmt['props'][0]['name']['name']
                tmp += f"$my{parent.className}->{propName} = new StdClass;\r\n"
        tmp += f"$my{parent.className}->{cur.fromObj} = $my{cur.className};\r\n"
        cur = parent
        parent = parent.parent
        ret +=tmp
    print(ret)

for i in range(len(class_ast)):
    classes_ast[class_ast[i]['name']['name']] = class_ast[i]

#根据f反查class
f2cTable = {}
#ban_function = ['YkN508','frZNkk','N3R1ow','N3R1ow','CCO4GN','LCG9b8','ILnKZX']
ban_function = []
know_children = {}
functions_ast = {}
for name,ast in classes_ast.items():
    for f in ast["stmts"]: 
        if f['nodeType'] == "Stmt_ClassMethod":
            class_method_name = f['name']['name']
            children_method_name = None
            fromObj = None
            if class_method_name == '__call':
               # extract([$name => 'nglEtPMT']);
                for stmt in f['stmts']:
                    if stmt['nodeType'] == 'Stmt_Expression':
                        expr = stmt['expr']
                        if expr['nodeType'] == 'Expr_FuncCall' and expr['name']['parts'][0]=='extract':
                            children_method_name = expr['args'][0]['value']['items'][0]['value']['value']
                            fromObj = ast['stmts'][0]['props'][0]['name']['name']
                    elif stmt['nodeType'] == 'Stmt_If' and get_funccall_name(stmt['cond']) == 'is_callable':
                        expr = stmt['cond']
                        class_method_name = expr['args'][0]['value']['items'][1]['value']['name']
                        break
                if fromObj != None and children_method_name!=None:
                    know_children[class_method_name] = [(fromObj,children_method_name)]
            f2cTable[class_method_name] = name
            functions_ast[class_method_name] = f
         

visit_function = {}
q = queue.SimpleQueue()
initState = Node(None,"__destruct",f2cTable['__destruct'],None)
q.put(initState)

while not q.empty():
    cur:Node = q.get()
   #print(cur)
   #循 环 剪 枝
    if hasattr(visit_function,cur.className+"::"+cur.funcname):
        continue
    else:
        visit_function[cur.className+"::"+cur.funcname] = True
       
       #黑 名 单 剪 枝
        if cur.funcname in ban_function:
            continue
        if cur.funcname in know_children.keys():
            for fromObj,child in know_children[cur.funcname]:
                q.put(Node(cur,child,f2cTable[child],fromObj))
            continue
           
       
        cur_function_ast = functions_ast[cur.funcname]
        nxt_function = ''
        if len(cur_function_ast['params']) > 0:
            cur_param_name = cur_function_ast['params'][0]['var']['name']

       #遍 历 当 前 函 数 方 法
        for stmt in cur_function_ast['stmts']:
            # xxx;
            if stmt['nodeType'] == 'Stmt_Expression':
                expr = stmt['expr']
                if expr['nodeType'] == 'Expr_ErrorSuppress':
                    expr = stmt['expr']['expr']
                if expr['nodeType'] == "Expr_Assign" and expr['var']['name'] == cur_param_name:
                    #@$Cz9slGovKv = md5($Cz9slGovKv);
                    if expr['expr']['nodeType'] == 'Expr_FuncCall':
                        iexpr = expr['expr']
                        if get_funccall_name(iexpr) in ['md5','sha1','crypt','base64_encode']:
                            break
                        else:
                            cur.operation += get_funccall_name(iexpr)
                   # @$DP1 = $WE;
                    elif expr['expr']['nodeType'] == 'Expr_Variable' and expr['expr']['name'] != cur_param_name:
                        break
            elif stmt['nodeType'] == 'Stmt_If':
                if stmt['cond']['nodeType'] == "Expr_FuncCall":
                    if get_funccall_name(stmt['cond']) == 'is_callable':
                        for istmt in stmt['stmts']:
                            if istmt['nodeType'] == "Stmt_Expression":
                                param_name = istmt['expr']['expr']['var']['name']['name']
                                nxt_function_name =  istmt['expr']['expr']['name']['name']
                       #print(param_name) 
                    q.put(Node(cur,nxt_function_name,f2cTable[nxt_function_name],param_name))
                elif stmt['cond']['nodeType'] == 'Expr_BinaryOp_Identical':
                    left = stmt['cond']['left']
                    if get_funccall_name(left) == 'stripos':
                        print("Ok")
                        printGraph(cur)
                        printExp(cur)
                        exit(0)