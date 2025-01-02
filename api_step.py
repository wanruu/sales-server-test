import requests as r
from swagger import Swagger
import pydash


swagger = Swagger("http://localhost:3000/api-doc-json")


class ApiStep:
    __continue_on_error = True
    __expected_status_code = 200
    __pre_process_callbacks = []
    __post_process_callbacks = []

    def __init__(self, method, path, path_params={}, query_params={}, headers={}, body={}):
        self.__method = method
        self.__path = path
        self.__path_params = path_params
        self.__query_params = query_params
        self.__headers = headers
        self.__body = body
    
    @property
    def response(self):
        return self.__response

    def expect(self, status_code):
        self.__expected_status_code = status_code

    def add_process(self, pre_or_post, callback):
        if pre_or_post == 'pre':
            self.__pre_process_callbacks.append(callback)
        elif pre_or_post == 'post':
            self.__post_process_callbacks.append(callback)
    
    def add_assertion(self, path, callback):
        self.__post_process_callbacks.append(lambda: callback(pydash.get(self.__response, path)))

    def run(self, validate_response=True):
        # pre process
        for callback in self.__pre_process_callbacks:
            ret = callback()
        
        # send api
        path = self.__path
        for key, value in self.__path_params.items():
            path = path.replace('{' + key + '}', value)
        response = r.request(
            method=self.__method, 
            url='http://localhost:3000'+path, 
            params=self.__query_params, 
            headers=self.__headers, 
            data=self.__body
        )
        self.__response = {
            "body": response.json(),
            "status_code": response.status_code,
            "headers": response.headers
        }

        # check response
        if response.status_code != self.__expected_status_code:
            print('❌', f"Expected status code {self.__expected_status_code}, but got {response.status_code}")
            if not self.__continue_on_error:
                return
        
        if validate_response:
            ret, msgs = swagger.check_response(
                path=self.__path, 
                method=self.__method, 
                status_code=str(self.__expected_status_code), 
                content_type=response.headers['Content-Type'].split(';')[0],
                response=response.json()
            )
            if ret:
                print('✔ 返回数据结构与接口定义一致')
            else:
                for msg in msgs:
                    print('❌', msg)
                if not self.__continue_on_error:
                    return
        
        # post process
        for callback in self.__post_process_callbacks:
            callback()

