namespace_temlate = """
namespace {ns_name} {{
    {code}
}}"""

class_template = """
class {class_name} {{
    {fields}
    {methods}
}}
"""

field_template = """
    {visibility} {field_type} ${field_name};"""

method_template = """
    {visibility} function {method_name}({method_args}) {{
        {code}
    }}"""

rand_interesting_code = [
    "@${input_value} = str_rot13(${input_value});\n",
    "@${input_value} = base64_decode(${input_value});\n",
    "@${input_value} = ucfirst(${input_value});\n",
    "@${input_value} = strrev(${input_value});\n",
    "@${input_value} = ${input_value};\n"
]

rand_fucking_code = [
    "@${input_value} = md5(${input_value});\n",
    "@${input_value} = crypt(${input_value}, '{rand_value}');\n",
    "@${input_value} = base64_encode(${input_value});\n",
    "@${input_value} = sha1(${input_value});\n",
    "@${input_value} = ${rand_value};\n"
]

normal_method_code = """if (is_callable([$this->{field_name}, '{next_method_name}'])) @$this->{field_name}->{next_method_name}(${input_value});"""

call_code =  """extract([$name => '{next_method_name}']);
        if (is_callable([$this->{field_name}, ${last_func_name}]))
            call_user_func([$this->{field_name}, ${last_func_name}], ...$value);"""

invoke_last_code = "@call_user_func($this->{field_name}, ['{rand_key}' => ${input_value}]);"

invoke_code = """$key = base64_decode('{b64encode_rand_key}');
        @$this->{field_name}->{next_method_name}($value[$key]);"""

end_code = """if(stripos(${input_value}, "/fumo") === 0) readfile(strtolower(${input_value}));"""