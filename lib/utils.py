import pydash


global_variables = {}


def set_global_variables(path, value):
    global global_variables
    global_variables = pydash.set_(global_variables, path, value)


def get_global_variables(path):
    global global_variables
    return pydash.get(global_variables, path)


def assertion(actual, operator, expected):
    if operator == '==' and actual != expected:
        print('❌ 断言失败：', actual, operator, expected)