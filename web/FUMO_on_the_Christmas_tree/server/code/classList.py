from php import phpClass, phpField, phpMethod
from typing import List

class classListNode:
    def __init__(self, class_object: phpClass) -> None:
        self.class_object = class_object
    
    def get_php_class(self) -> phpClass:
        return self.class_object
    
    def set_php_class(self, class_object: phpClass) -> None:
        self.class_object = class_object
    
    def __str__(self) -> str:
        field_name_list = []
        field_list = self.class_object.get_field_list()
        for field in field_list:
            field_name_list.append(field.field_name)
        
        method_name_list = []
        method_list = self.class_object.get_method_list()
        for method in method_list:
            method_name_list.append(method.method_name)

        class_name = self.class_object.class_name

        return str({
            class_name : {
                "fields" : field_name_list,
                "methods" : method_name_list
            }
        })

class classList:
    def __init__(self, list: List[classListNode] = None) -> None:
        self.list = list if list != None else []
    
    def append(self, node: classListNode) -> None:
        self.list.append(node)

    def __iter__(self):
        self._iter = iter(self.list)
        return self._iter
    
    def __next__(self) -> list:
        return self._iter.next()

    def __str__(self) -> str:
        return str(self.list)
    
    def __getitem__(self, id: int) -> classListNode:
        try:
            return self.list[id]
        except:
            return None
    
    def __len__(self) -> int:
        return len(self.list)