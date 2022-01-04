import random
from sys import argv
from typing import List
from base64 import b64encode

import phpCodeTemplate as tp
from classList import classList, classListNode
from php import phpClass, phpMethod, phpField, phpMagicMethodType, phpMagicMethodArgs

def get_random_str():
    randomlength = random.randint(6, 10)
    random_str = ''
    base_str1 = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz'
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
    length1 = len(base_str1) - 1
    length = len(base_str) - 1
    random_str = base_str1[random.randint(0, length1)]
    for _ in range(randomlength-1):
        random_str += base_str[random.randint(0, length)]
    return random_str

ALL_CLASS_LIST = []
ROOT_CHAIN_LEN = 20
RING_CHAIN_LEN = 10
ROOT_POP_CHAIN = classList([])

def fill_in_methods(class_list: classList, is_root: bool = False, is_ring: bool = False):

    FILLED_MAGIC_METHOD_ROUND = 0
    CLASS_LIST_LEN = len(class_list)

    def can_fill_in_magic_method(method_type: phpMagicMethodType, id: int, list_len: int) -> bool:
        return (
            method_type != phpMagicMethodType.notMagicMethod and 
            method_type != phpMagicMethodType.toString and
            id >= 2 and 
            id <= list_len - 3 and 
            FILLED_MAGIC_METHOD_ROUND == 0
        )
    
    def fill_method_in_list(class_list: classList, i: int):
        nonlocal FILLED_MAGIC_METHOD_ROUND

        def rand_magic_method_type_in_list() -> phpMagicMethodType:
            i = random.randint(0, 50)
            i = [0, 0, 0, 1, 3][i % 5]
            return phpMagicMethodType(i)

        if ((i > 0 and i < CLASS_LIST_LEN - 1) or not is_root):
            method_type = rand_magic_method_type_in_list()
            if (can_fill_in_magic_method(method_type, i, CLASS_LIST_LEN)):
                method = phpMethod(
                    1, "__" + method_type.name, method_type, phpMagicMethodArgs[method_type.name].value
                )
                class_list[i].get_php_class().add_method(method)

                FILLED_MAGIC_METHOD_ROUND = 2
            else:
                method = phpMethod(
                    1, get_random_str(), phpMagicMethodType.notMagicMethod, [get_random_str()]
                )
                class_list[i].get_php_class().add_method(method)

                if (FILLED_MAGIC_METHOD_ROUND > 0):
                    FILLED_MAGIC_METHOD_ROUND -= 1

        elif (i == CLASS_LIST_LEN - 1):
            method = phpMethod(
                1, get_random_str(), phpMagicMethodType.notMagicMethod, [get_random_str()]
            )
            class_list[i].get_php_class().add_method(method)

        else:
            method = phpMethod(
                1, "__destruct", phpMagicMethodType.destruct, phpMagicMethodArgs.destruct.value
            )
            class_list[i].get_php_class().add_method(method)

    def fill_method_in_ring(class_list: classList, i: int):
        nonlocal FILLED_MAGIC_METHOD_ROUND

        def rand_magic_method_type_in_list() -> phpMagicMethodType:
            i = random.randint(0, 50)
            i = [0, 0, 0, 1, 3][i % 5]
            return phpMagicMethodType(i)

        if ((i > 0 and i < CLASS_LIST_LEN - 1) or not is_root):
            method_type = rand_magic_method_type_in_list()
            if (can_fill_in_magic_method(method_type, i, CLASS_LIST_LEN)):
                method = phpMethod(
                    1, "__" + method_type.name, method_type, phpMagicMethodArgs[method_type.name].value
                )
                class_list[i].get_php_class().add_method(method)

                FILLED_MAGIC_METHOD_ROUND = 2
            else:
                method = phpMethod(
                    1, get_random_str(), phpMagicMethodType.notMagicMethod, [get_random_str()]
                )
                class_list[i].get_php_class().add_method(method)

                if (FILLED_MAGIC_METHOD_ROUND > 0):
                    FILLED_MAGIC_METHOD_ROUND -= 1

        elif (i == CLASS_LIST_LEN - 1):
            method = phpMethod(
                1, get_random_str(), phpMagicMethodType.notMagicMethod, [get_random_str()]
            )
            class_list[i].get_php_class().add_method(method)

        else:
            method = phpMethod(
                1, "__destruct", phpMagicMethodType.destruct, phpMagicMethodArgs.destruct.value
            )
            class_list[i].get_php_class().add_method(method)

    if (is_ring):
        func = fill_method_in_ring
    else:
        func = fill_method_in_list

    for i in range(0, CLASS_LIST_LEN):
        func(class_list, i)

def fill_code_in_method(class_list: classList, is_alive: bool = False, is_root: bool = False):
    global ROOT_POP_CHAIN

    HAS_BE_DEAD = False
    LAST_FUNC_NAME = ""
    RAND_INVOKE_KEY = ""
    CLASS_LIST_LEN = len(class_list)

    def get_other_code(id: int) -> str:
        nonlocal HAS_BE_DEAD
        rand_id = random.randint(0, 4)

        if (is_alive):
            other_code = tp.rand_interesting_code[rand_id]
        elif (HAS_BE_DEAD or CLASS_LIST_LEN - id > 3):
            other_code = tp.rand_interesting_code[rand_id]
        else:
            other_code = tp.rand_fucking_code[rand_id]
            HAS_BE_DEAD = True
        return other_code

    for i in range(0, CLASS_LIST_LEN):
        if (i == CLASS_LIST_LEN - 1): # 填充链中最后一个类的代码
            self_class = class_list[i].get_php_class()

            field = phpField(
                1, get_random_str(), "object"
            )

            if is_root or random.randint(0, 1) == 1:
                code = tp.end_code.format(
                    input_value = self_class.get_method_with_id(0).get_args_list()[0]
                )
            else:
                code = tp.normal_method_code.format(
                    field_name = field.field_name,
                    next_method_name = ROOT_POP_CHAIN[1].get_php_class().get_method_with_id(0).method_name,
                    input_value = get_random_str()
                )

            class_list[i].get_php_class().add_field(field)
            class_list[i].get_php_class().get_method_with_id(0).set_code(code)
            
        elif (i == 0): # 填充链中第一个类的代码
            self_class = class_list[i].get_php_class()
            next_class = class_list[i + 1].get_php_class()

            field = phpField(
                1, get_random_str(), "object"
            )

            if (is_root):
                code = tp.normal_method_code.format(
                    field_name       = field.field_name,
                    next_method_name = next_class.get_method_with_id(0).method_name,
                    input_value      = "_GET['{0}']".format(get_random_str())
                )
            else:
                other_code = get_other_code(i)
                code = (other_code + "\t\t" + tp.normal_method_code).format(
                    field_name = field.field_name,
                    next_method_name = next_class.get_method_with_id(0).method_name,
                    input_value = self_class.get_method_with_id(0).get_args_list()[0],
                    rand_value = get_random_str()
                )

            class_list[i].get_php_class().add_field(field)
            class_list[i].get_php_class().get_method_with_id(0).set_code(code)

        else: # 填充链中其它类的代码
            next_class = class_list[i + 1].get_php_class()
            last_class = class_list[i - 1].get_php_class()
            self_class = class_list[i].get_php_class()

            self_class_method_type = self_class.get_method_with_id(0).get_magic_type()
            next_class_method_type = next_class.get_method_with_id(0).get_magic_type()
            last_class_method_type = last_class.get_method_with_id(0).get_magic_type()

            if (self_class_method_type != phpMagicMethodType.notMagicMethod): # 但自身是魔法方法时
                if (self_class_method_type == phpMagicMethodType.call): # __call
                    field = phpField(
                        1, get_random_str(), "object"
                    )

                    code = tp.call_code.format(
                        field_name = field.field_name,
                        next_method_name = next_class.get_method_with_id(0).method_name,
                        last_func_name = LAST_FUNC_NAME
                    )

                elif (self_class_method_type == phpMagicMethodType.invoke): # __invoke
                    field = phpField(
                        1, get_random_str(), "object"
                    )

                    code = tp.invoke_code.format(
                        field_name = field.field_name,
                        next_method_name = next_class.get_method_with_id(0).method_name,
                        b64encode_rand_key = b64encode(RAND_INVOKE_KEY.encode()).decode("UTF-8")
                    )

            elif (next_class_method_type != phpMagicMethodType.notMagicMethod): # 当下一个类是魔法方法时
                if (next_class_method_type == phpMagicMethodType.call): # __call
                    LAST_FUNC_NAME = get_random_str()

                    field = phpField(
                        1, get_random_str(), "object"
                    )

                    other_code = get_other_code(i)

                    code = (other_code + "\t\t" + tp.normal_method_code).format(
                        field_name = field.field_name,
                        next_method_name = LAST_FUNC_NAME,
                        input_value = self_class.get_method_with_id(0).get_args_list()[0],
                        rand_value = get_random_str()
                    )

                elif (next_class_method_type == phpMagicMethodType.invoke): # __invoke
                    RAND_INVOKE_KEY = get_random_str()

                    field = phpField(
                        1, get_random_str(), "object"
                    )

                    code = tp.invoke_last_code.format(
                        field_name = field.field_name,
                        rand_key = RAND_INVOKE_KEY,
                        input_value = self_class.get_method_with_id(0).get_args_list()[0],
                        rand_value = get_random_str()
                    )

            elif (last_class_method_type != phpMagicMethodType.notMagicMethod and # 当上一个类是非__destruct的魔法方法时
                  last_class_method_type != phpMagicMethodType.destruct
                ):
                if (last_class_method_type == phpMagicMethodType.call):
                    field = phpField(
                        1, get_random_str(), "object"
                    )

                    other_code = get_other_code(i)

                    code = (other_code + "\t\t" + tp.normal_method_code).format(
                        field_name = field.field_name,
                        next_method_name = next_class.get_method_with_id(0).method_name,
                        input_value = self_class.get_method_with_id(0).get_args_list()[0],
                        rand_value = get_random_str()
                    )

                    LAST_FUNC_NAME = ""

                elif (last_class_method_type == phpMagicMethodType.invoke):
                    field = phpField(
                        1, get_random_str(), "object"
                    )

                    other_code = get_other_code(i)

                    code = (other_code + "\t\t" + tp.normal_method_code).format(
                        field_name = field.field_name,
                        next_method_name = next_class.get_method_with_id(0).method_name,
                        input_value = self_class.get_method_with_id(0).get_args_list()[0],
                        rand_value = get_random_str()
                    )

                    RAND_INVOKE_KEY = ""

            else: # 上下以及自身都是普通方法时
                field = phpField(
                    1, get_random_str(), "object"
                )

                other_code = get_other_code(i)

                code = (other_code + "\t\t" + tp.normal_method_code).format(
                    field_name = field.field_name,
                    next_method_name = next_class.get_method_with_id(0).method_name,
                    input_value = self_class.get_method_with_id(0).get_args_list()[0],
                        rand_value = get_random_str()
                )

            class_list[i].get_php_class().add_field(field)
            class_list[i].get_php_class().get_method_with_id(0).set_code(code)

def create_class_list(list_len: int = ROOT_CHAIN_LEN, is_alive: bool = False, is_root: bool = False):
    class_list = classList()

    for _ in range(0, list_len):
        class_object = phpClass(
            get_random_str()
        )
        node = classListNode(class_object)
        class_list.append(node)

    fill_in_methods(class_list, is_root)
    fill_code_in_method(class_list, is_alive, is_root)
    return class_list

def link_list_2_tree(insert_id: int, root_list: classList, insert_list: classList):
    already_insert_class = root_list[insert_id].get_php_class()
    already_insert_method = root_list[insert_id].get_php_class().get_method_with_id(0)
    already_insert_method_args = root_list[insert_id].get_php_class().get_method_with_id(0).get_args_list()[0]
    next_method_name = insert_list[0].get_php_class().get_method_with_id(0).method_name

    field = phpField(
        1, get_random_str(), "object"
    )

    code = tp.normal_method_code.format(
        field_name = field.field_name,
        next_method_name = next_method_name,
        input_value = already_insert_method_args
    )
    
    if (random.randint(0, 1) == 0):
        new_code = code + "\n\t\t" + already_insert_method.get_code()
    else:
        new_code = already_insert_method.get_code() + "\n\t\t" + code
    
    already_insert_method.set_code(new_code)

    already_insert_class.add_field(field)

def create_class_tree(root_list: classList):
    global ALL_CLASS_LIST

    root_list_len = len(root_list)

    for i in range(0, root_list_len):
        note_class = root_list[i].get_php_class()
        class_method_type = note_class.get_method_with_id(0).get_magic_type()
        if (class_method_type == phpMagicMethodType.notMagicMethod):
            branch_list_len = root_list_len - random.randint(4, 5)
            if (branch_list_len > 1 and i < root_list_len - 2 and len(ALL_CLASS_LIST) < 14000):
                branch_list = create_class_list(branch_list_len)
                link_list_2_tree(i, root_list, branch_list)
                ALL_CLASS_LIST += branch_list.list
                create_class_tree(branch_list)
            else:
                break
        else:
            continue

if __name__ == '__main__':
    php_sandbox_path = argv[1]

    root_list = create_class_list(
        is_alive = True,
        is_root = True
    )

    ROOT_POP_CHAIN = root_list
    ALL_CLASS_LIST += root_list.list
    create_class_tree(root_list)

    random.shuffle(ALL_CLASS_LIST)
    all_list = classList(
        ALL_CLASS_LIST
    )

    php_class_file_path = php_sandbox_path + "class.php"
    with open(php_class_file_path, "w") as fp:
        class_str = ""
        fp.write("<?php")

        for class_note in all_list:
            class_str += str(class_note.get_php_class())
        
        fp.write(tp.namespace_temlate.format(
            code = class_str,
            ns_name = "christmasTree"
        ))