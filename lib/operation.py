from abc import ABC, abstractmethod
from lib.utils import set_global_variables, custom_get, custom_replace
import json


class Operation(ABC):
    @abstractmethod
    def run(self, src_object):
        pass

class AssertEqualOperation(Operation):
    def __init__(self, path: str, value_str: str):
        self.path = path
        self.value_str = str(value_str)

    def run(self, src_object):
        actual_value = custom_get(src_object, self.path)
        replaced_value = custom_replace(self.value_str, src_object)
        try:
            msg = f"{self.path} 等于 {replaced_value}"
            if actual_value is None:
                return replaced_value == 'None', msg
            if type(actual_value) == dict or type(actual_value) == list:
                return actual_value == json.loads(replaced_value), f"{self.path} 等于 {json.dumps(json.loads(replaced_value))}"
            elif type(actual_value) == int or type(actual_value) == float:
                return str(actual_value) == replaced_value, msg
            else:
                return actual_value == replaced_value, msg
        except Exception as e:
            return False, e

class SetGlobalVariableOperation(Operation):
    def __init__(self, variable_name: str, value_str: str):
        self.variable_name = variable_name
        self.value_str = value_str

    def run(self, src_object):
        try:
            new_value = custom_replace(self.value_str, src_object)
            set_global_variables(self.variable_name, new_value)
            return True, f"设置全局变量 {self.variable_name} 成功"
        except Exception as e:
            return False, f"设置全局变量 {self.variable_name} 失败: {e}"