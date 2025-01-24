from lib.step import Step
from typing import List
import datetime
from lib.html_saver import HtmlSaver


html_saver = HtmlSaver()


class Testcase:
    def __init__(self, name, description=None, steps: List[Step] = []):
        self.__name = name
        self.__dirname = name + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.__description = description
        self.__steps = steps

        names = set()
        for index, step in enumerate(self.__steps):
            if step.name is None:
                step.name = f"Step {index+1}"
            if step.name in names:
                for i in range(1, 1000):
                    new_name = f"{step.name} ({i})"
                    if new_name not in names:
                        step.name = new_name
                        break
            names.add(step.name)

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = value

    @property
    def dirname(self):
        return self.__dirname

    @property
    def steps(self):
        return self.__steps

    def add_step(self, step: Step):
        names = set(map(lambda s: s.name, self.steps))
        if step.name is None:
            step.name = f"Step {len(self.__steps)+1}"
        if step.name in names:
            for i in range(1, 1000):
                new_name = f"{step.name} ({i})"
                if new_name not in names:
                    step.name = new_name
                    break
        self.__steps.append(step)

    def run(self):
        src_object = []
        for step in self.__steps:
            step.src_object = src_object + [step]
            step.run()
            src_object.append(step)

        html_saver.add_testcase(self)
        html_saver.save()
