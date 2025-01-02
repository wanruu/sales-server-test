import requests
import pydash
from jsonschema import Draft202012Validator
from lib.utils import get_global_variables

swagger_json = requests.get('http://localhost:3000/api-doc-json').json()


class Api:
    # __pre_callbacks = []
    # __post_callbacks = []
    # __request = { "method": "", "path": "", "body": {}, "headers": {}, "path_params": {}, "query_params": {} }
    # __response = None
    # __expected_status_code = 200
    __url = 'http://localhost:3000'
    
    __COUNTER = 1

    def __init__(self, method, path, path_params={}, query_params={}, headers={}, body={}, expected_status_code=None):
        self.__request = {
            "method": method,
            "path": path,
            "body": body,
            "headers": pydash.merge(
                { "Authorization" : f"Bearer {get_global_variables(['access_token'])}" },
                headers
            ),
            "path_params": path_params,
            "query_params": query_params,
        }
        if expected_status_code is None:
            if method == 'delete':
                self.__expected_status_code = 204
            elif method == 'post':
                self.__expected_status_code = 201
            else:
                self.__expected_status_code = 200
        else:
            self.__expected_status_code = int(expected_status_code)
        self.__pre_callbacks = []
        self.__post_callbacks = []


    def get_variable(self, path):
        obj = { "response": self.__response, "request": self.__request }
        return pydash.get(obj, path)

    def add_operation(self, pre_or_post, callback):
        if pre_or_post == 'pre':
            self.__pre_callbacks.append(callback)
        elif pre_or_post == 'post':
            self.__post_callbacks.append(callback)

    def run(self):
        # path
        path = self.__request["path"]
        for key, value in self.__request["path_params"].items():
            path = path.replace('{' + key + '}', str(value))
        
        # print request
        print('|'.ljust(32, '-') + '|')
        print(f"| 第{Api.__COUNTER}个接口".ljust(8) + f"{self.__request['method']} {path}".ljust(20) + '|')
        print('|'.ljust(32, '-') + '|')
        Api.__COUNTER += 1
        
        # reset response
        self.__response = None
        
        # pre process
        for callback in self.__pre_callbacks:
            try:
                callback(self)
            except Exception as e:
                print('❌', f"前置操作失败：{e}")
        
        # send api
        response = requests.request(
            method=self.__request["method"], 
            url=self.__url + path, 
            params=self.__request["query_params"], 
            headers=self.__request["headers"], 
            json=self.__request["body"]
        )
        self.__response = {
            "body": '' if response.text == '' else response.json(),
            "code": response.status_code,
            "headers": response.headers,
        }

        # check response
        self.__validate_response()

        # post process
        for callback in self.__post_callbacks:
            try:
                callback(self)
            except Exception as e:
                print('❌', f"后置操作失败：{e}")

    def __validate_response(self):
        if (self.__response is None):
            print('❌ 无法获取响应')

        if self.__response["code"] != self.__expected_status_code:
            print('❌', f"预期状态码：{self.__expected_status_code}，实际状态码：{self.__response['code']}.")

        try:
            path = self.__request["path"]
            method = self.__request["method"]
            code = self.__expected_status_code
            content_type = self.__response["headers"]['Content-Type'].split(';')[0]
            content = swagger_json["paths"][path][method]['responses'][str(code)]['content'][content_type]
        except Exception:
            if self.__response["code"] == 204:
                print('✔ 返回数据结构与接口定义一致')
            else:
                print('❌', '接口定义中没有找到返回数据的定义')
            return

        if 'schema' in content:
            schema = pydash.merge(content['schema'], {"components": swagger_json["components"]})
            validator = Draft202012Validator(schema)
        else:
            raise Exception('Not implemented')
        
        errors = validator.iter_errors(self.__response["body"])
        ret = True
        for error in sorted(errors, key=str):
            print('❌', f'{error.json_path}校验失败：', error.message)
            ret = False
        if ret:
            print('✔ 返回数据结构与接口定义一致')

    def set_request(self, path, value):
        pydash.set_(self.__request, path, value)