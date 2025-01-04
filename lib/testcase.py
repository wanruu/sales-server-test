from lib.step import Step
from typing import List

class Testcase:
    def __init__(self, name, description=None, steps:List[Step]=[]):
        self.__name = name
        self.__description = description
        self.__steps = steps
        self.__success_count = 0
        
        for (index, step) in enumerate(self.__steps):
            if step.name is None:
                step.name = f'Step {index+1}'

    def get_variable(self, path: str):
        path_list = path.split('.')
        if len(path_list) == 0:
            return None
        return self.__steps[int(path_list[0])].get_variable('.'.join(path[1:]))
    
    def add_step(self, step: Step):
        if step.name is None:
            step.name = f'Step {len(self.__steps)+1}'
        self.__steps.append(step)
    
    def run(self):
        src_object = []
        for step in self.__steps:
            src_object.append(step)
            step.src_object = src_object
            ret, pre_operation_results, validation_results, post_operation_results = step.run()
            print(ret)