import requests
import pydash
from jsonschema import Draft202012Validator


swagger_json = requests.get('http://localhost:3000/api-doc-json').json()


class ApiStep:
    __pre_process_callbacks = []
    __post_process_callbacks = []
    __response = None
    __url = 'http://localhost:3000'
    __base_headers = {}

    def __init__(self, method, path, path_params={}, query_params={}, headers={}, body={}, code=200):
        self.__method = method
        self.__path = path
        self.__path_params = path_params
        self.__query_params = query_params
        self.__headers = pydash.merge(self.__base_headers, headers)
        self.__body = body
        self.__expected_status_code = code
    
    @property
    def response(self):
        return self.__response

    @classmethod
    def update_headers(cls, headers):
        cls.__base_headers = pydash.merge(cls.__base_headers, headers)

    def get_variable(self, path):
        paths = path.split('.')
        obj = {
            "response": {
                "body": self.__response.json(),
                "code": str(self.__response.status_code)
            },
            "request": {
                "body": self.__body,
                "headers": self.__headers,
                "path_params": self.__path_params,
                "query_params": self.__query_params
            }
        }
        return pydash.get(obj, paths)

    def expect(self, status_code):
        self.__expected_status_code = status_code

    def add_process(self, pre_or_post, callback):
        if pre_or_post == 'pre':
            self.__pre_process_callbacks.append(callback)
        elif pre_or_post == 'post':
            self.__post_process_callbacks.append(callback)

    def run(self):
        # pre process
        for callback in self.__pre_process_callbacks:
            ret = callback(self)
        
        # send api
        path = self.__path
        for key, value in self.__path_params.items():
            path = path.replace('{' + key + '}', value)
        self.__response = requests.request(
            method=self.__method, 
            url=self.__url + path, 
            params=self.__query_params, 
            headers=self.__headers, 
            data=self.__body
        )

        # check response
        self.__validate_response()

        # post process
        for callback in self.__post_process_callbacks:
            callback(self)

    def __validate_response(self):
        if (self.__response is None):
            print('❌ 无法获取响应')

        status_code = str(self.__response.status_code)
        if status_code != str(self.__expected_status_code):
            print('❌', f"预期状态码：{self.__expected_status_code}，实际状态码：{status_code}.")
        
        try:
            content_type = self.__response.headers['Content-Type'].split(';')[0]
            content = swagger_json["paths"][self.__path][self.__method]['responses'][str(self.__expected_status_code)]['content'][content_type]
        except Exception:
            print('❌', '接口定义中没有找到返回数据的定义')
            return

        if 'schema' in content:
            schema = pydash.merge(content['schema'], {"components": swagger_json["components"]})
            validator = Draft202012Validator(schema)
        else:
            print('todo!')
        
        errors = validator.iter_errors(self.__response.json())
        ret = True
        for error in sorted(errors, key=str):
            print('❌', error.message)
            ret = False
        if ret:
            print('✔ 返回数据结构与接口定义一致')