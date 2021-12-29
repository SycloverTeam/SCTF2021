from typing import List
from enum import Enum
from phpCodeTemplate import class_template, field_template, method_template

class phpVisibility(Enum):
    public = 1
    protected = 2
    private = 3

class phpMagicMethodType(Enum):
    call = 1
    toString = 2
    invoke = 3
    destruct = -1
    notMagicMethod = 0

class phpMagicMethodArgs(Enum):
    call = ["name", "value"]
    get = ["name"]
    invoke = ["value"]
    toString = []
    destruct = []
    notMagicMethod = []

class phpField:
    def __init__(self, visibility: phpVisibility, name: str, field_type: str) -> None:
        self.visibility = phpVisibility(visibility)
        self.field_name = name
        self.field_type = field_type
    
    def __str__(self) -> str:
        return field_template.format(
            visibility = self.visibility.name,
            field_name = self.field_name,
            field_type = self.field_type
        )

class phpMethod:
    def __init__(self, visibility: phpVisibility, name: str, magic_type: phpMagicMethodType, args: List[str] = None, code: str = "") -> None:
        self.visibility = phpVisibility(visibility)
        self.method_name = name
        self.code = code
        self.args = args if args != None else []
        self.magic_type = magic_type
    
    def set_method_name(self, name: str):
        self.method_name = name

    def set_code(self, code: str):
        self.code = code
    
    def append_code(self, code: str):
        self.code += "\n\t\t" + code
    
    def get_code(self):
        return self.code
    
    def get_magic_type(self):
        return self.magic_type
    
    def get_args_list(self):
        return self.args

    def __str__(self) -> str:
        args_code = ""
        for arg in self.args:
            args_code += "${arg},".format(arg = arg)
        if ',' in args_code:
            args_code = args_code[:-1]

        return method_template.format(
            visibility = self.visibility.name,
            method_name = self.method_name,
            code = self.code,
            method_args = args_code 
        )

class phpClass:

    def __init__(self, name: str, fields: List[phpField] = None, methods: List[phpMethod] = None) -> None:
        self.class_name = name
        self.fields = fields if fields != None else []
        self.methods = methods if methods != None else []

    def add_field(self, field: phpField):
        self.fields.append(field)
    
    def set_field(self, id: int, field: phpField):
        self.fields[id] = field
    
    def get_field_with_id(self, id: int) -> phpField:
        try:
            return self.fields[id]
        except:
            return None
    
    def get_field_list(self) -> List[phpField]:
        return self.fields
    
    def add_method(self, method: phpMethod):
        self.methods.append(method)
    
    def set_method(self, id: int, method: phpMethod):
        self.methods[id] = method
    
    def get_method_with_id(self, id: int) -> phpMethod:
        try:
            return self.methods[id]
        except:
            return None
    
    def get_method_with_name(self, name: str) -> phpMethod:
        for method in self.get_method_list():
            if (name == method.method_name):
                return method
        
        return None
    
    def get_method_list(self) -> List[phpMethod]:
        return self.methods

    def __str__(self) -> str:
        field_code = ""
        for field in self.fields:
            field_code += str(field)
        
        method_code = ""
        for method in self.methods:
            method_code += str(method)

        class_code = class_template.format(
            class_name = self.class_name,
            fields = field_code,
            methods = method_code
        )
        return class_code