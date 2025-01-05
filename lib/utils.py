import pydash
import re
import json

global_variables = {}


def set_global_variables(path, value):
    global global_variables
    global_variables = pydash.set_(global_variables, path, value)


def get_global_variables(path):
    global global_variables
    if path == "":
        return global_variables
    return pydash.get(global_variables, path)


# get value from object by path
def custom_get(obj: any, path: str):
    if path == "":
        return obj

    result = obj
    path_list = path.split(".")
    for path_item in path_list:
        if result is None:
            return None

        if path_item == "length":
            if type(result) == dict or type(result) == list:
                result = len(result)
            else:
                result = obj.length
        elif type(result) == dict:
            result = result.get(path_item)
        elif type(result) == list:
            result = result[int(path_item)]
        else:
            result = getattr(result, path_item)

    return result


# replace {{value}} in object by path
def custom_replace(string: str, src_object: any):
    for match in re.findall(r"{{[a-zA-Z0-9_\.]+}}", string):
        value = custom_get(src_object, match[2:-2])
        if type(value) == str or type(value) == int or type(value) == float:
            string = string.replace(match, str(value))
        elif type(value) == bool:
            string = string.replace(match, str(value).lower())
        elif value is None:
            string = string.replace(match, "null")
        elif type(value) == dict:
            string = string.replace(match, json.dumps(value))
        else:
            raise Exception("未实现")
    return string
