import requests as r
from swagger import Swagger


swagger = Swagger("http://localhost:3000/api-doc-json")


class ApiStep:
    continue_on_error = True
    expected_status_code = 200

    def __init__(self, method, path, path_params={}, query_params={}, headers={}, body={}):
        self.method = method
        self.path = path
        self.path_params = path_params
        self.query_params = query_params
        self.headers = headers
        self.body = body

    def expect(self, status_code):
        self.expected_status_code = status_code
    
    def run(self):
        path = self.path
        for key, value in self.path_params.items():
            path = path.replace('{' + key + '}', value)
        response = r.request(
            method=self.method, 
            url='http://localhost:3000'+path, 
            params=self.query_params, 
            headers=self.headers, 
            data=self.body
        )
        
        if response.status_code != self.expected_status_code:
            print(f"Expected status code {self.expected_status_code}, but got {response.status_code}")
            if not self.continue_on_error:
                return
        
        ret, msgs = swagger.check_response(
            path=self.path, 
            method=self.method, 
            status_code=str(self.expected_status_code), 
            content_type=response.headers['Content-Type'].split(';')[0],
            response=response.json()
        )
        if ret:
            print('返回数据结构与接口定义一致')
        else:
            for msg in msgs:
                print(msg)
