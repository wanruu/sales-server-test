from lib.step import Step
from typing import List
import os
from lib.resources import report_root, latest, latest_filepath, max_latest_length
import json
import datetime

class Testcase:
    def __init__(self, name, description=None, steps:List[Step]=[]):
        self.__name = name
        self.__dirname = name + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.__description = description
        self.__steps = steps
        self.__success_count = 0
        
        names = set()
        for (index, step) in enumerate(self.__steps):
            if step.name is None:
                step.name = f'Step {index+1}'
            if step.name in names:
                for i in range(1, 1000):
                    new_name = f'{step.name} ({i})'
                    if new_name not in names:
                        step.name = new_name
                        break
            names.add(step.name)
        
        self.__dirpath = os.path.join(report_root, self.__dirname)
        if (not os.path.exists(self.__dirpath)):
            os.mkdir(self.__dirpath)

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
        self.__success_count = 0

        src_object = []
        for index, step in enumerate(self.__steps):
            step.src_object = src_object + [step]
            step.run()
            src_object.append(step)
            if step.success:
                self.__success_count += 1

            self.__save_step(index)
        self.__save_self()

    def __save_step(self, step_index):
        header = '''
            <head>
                <link rel="stylesheet" href="../base.css" />
                <script src="../script.js"></script>
            </head>
        '''
        step: Step = self.__steps[step_index]
        body = step.html_body()
        if (step_index == 0):
            prev_button = '<button disabled>Previous</button>'
        else:
            prev_button = f'<button onclick="window.location.href=\'./{self.__steps[step_index-1].name}.html\'">Previous</button>'
        if (step_index == len(self.__steps)-1):
            next_button = '<button disabled>Next</button>'
        else:
            next_button = f'<button onclick="window.location.href=\'./{self.__steps[step_index+1].name}.html\'">Next</button>'
        footer = f'''
            <div style="justify-content: space-between; display: flex;">
                <button onclick="window.location.href='./index.html'">Back</button>
                <span>{prev_button} {next_button}</span>
            </div>
        '''

        filepath = os.path.join(self.__dirpath, f'{step.name}.html')
        with open(filepath, 'w+') as f:
            f.write(f'<!DOCTYPE html><html>{header}<body><h1>{self.__name}</h1>{body}{footer}</body></html>')

    def __save_self(self):
        header = '''
            <head>
                <title>Testcase1</title>
                <link rel="stylesheet" href="../base.css" />
            </head>
        '''
        body = self.html_body()
        filepath = os.path.join(self.__dirpath, 'index.html')
        with open(filepath, 'w+') as f:
            f.write(f'<!DOCTYPE html><html>{header}<body>{body}</body></html>')
        
        # update latest
        latest.insert(0, {
            "name": self.__name,
            "dirname": self.__dirname,
            "total_steps": len(self.__steps),
            "success_steps": self.__success_count
        })
        if len(latest) > max_latest_length:
            latest.pop()
        def gen_latest_row(item):
            svg_name = 'success' if item["total_steps"] == item["success_steps"] else 'failed'
            return f'''
                <tr>
                    <td><img src="./svgs/{svg_name}.svg" width="20" height="20" /></td>
                    <td><a href="{item["dirname"]}/index.html">{item["name"]}</a></td>
                    <td>{item["success_steps"] / item["total_steps"] * 100:.1f}%</td>
                </tr>
            '''
        latest_html = f'''<!DOCTYPE html>
            <html>
            <head>
                <title>Test Report</title>
                <link rel="stylesheet" href="base.css" />
            </head>
            <body>
                <h1>Test Report</h1>
                <table>
                    <tr>
                        <th></th>
                        <th>Testcase</th>
                        <th>Pass Rate</th>
                    </tr>
                    {''.join([gen_latest_row(item) for item in latest])}
                </table>
            </body>
            </html>'''
        with open(os.path.join(report_root, 'index.html'), 'w+') as f:
            f.write(latest_html)
        with open(latest_filepath, 'w+') as f:
            json.dump(latest, f)

    def html_body(self):
        table_rows = "".join([f'''
                                <tr>
                                    <td>{
                                        '<img src="../svgs/success.svg" width="20" height="20" />'
                                        if step.success else 
                                        '<img src="../svgs/failed.svg" width="20" height="20" />'}
                                    </td>
                                    <td><a href="{step.name}.html">{step.name}</a></td>
                                    <td>{step.method.upper()} {step.request['url']}</td>
                                    <td>{step.response['status_code']}</td>
                                    <td>{step.response['response_time']}s</td>
                                </tr>
                            ''' for step in self.__steps])
        description = f'<p>{self.__description}</p>' if self.__description else ""
        return f'''
            <h1>{self.__name}</h1>
            {description}
            <table>
                <tr>
                    <th></th>
                    <th>Step</th>
                    <th>API</th>
                    <th>Status Code</th>
                    <th>Response Time</th>
                </tr>
                {table_rows}
            </table>
            <br/>
            <button onclick="window.location.href='../index.html'">Back</button>
        '''