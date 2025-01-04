import requests
import pydash
from jsonschema import Draft202012Validator
from lib.utils import get_global_variables, custom_replace
from typing import Tuple, List
import json
from lib.operation import Operation

swagger_json = requests.get('http://localhost:3000/api-doc-json').json()

DEFAULT_STATUS_CODE_DICT = {
    'delete': 204,
    'get': 200,
    'post': 201,
    'put': 200,
    'patch': 200,
}

class Step:
    def __init__(self, method:str, path:str, name:str=None, path_params:str='{}', query_params:str='{}', headers:str='{}', body:str='{}', expected_status_code=None):
        self.__name = name
        self.__method = method
        self.__path = path
        self.__url_prefix = 'http://localhost:3000'
        self.__headers_str = headers
        self.__body_str = body
        self.__path_params_str = path_params
        self.__query_params_str = query_params
        self.__expected_status_code = int(expected_status_code) if expected_status_code is not None else DEFAULT_STATUS_CODE_DICT.get(method)

        self.__pre_operations = []
        self.__post_operations = []
        self.__src_object = self  # for get variable by path

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def response(self):
        return self.__response

    @property
    def request(self):
        return self.__request

    @property
    def src_object(self):
        return self.__src_object

    @src_object.setter
    def src_object(self, value):
        self.__src_object = value

    @property
    def success(self):
        return self.__success

    @property
    def method(self):
        return self.__method

    def add_pre_operation(self, operation: Operation):
        self.__pre_operations.append(operation)

    def add_post_operation(self, operation: Operation):
        self.__post_operations.append(operation)

    # run step, return success and 3 lists of messages
    # also this will set self.__response and self.__request
    def run(self):
        overall_success = True
        
        # pre operations
        ret, pre_operation_results = self.__run_operations(self.__pre_operations)
        overall_success = overall_success and ret

        # send api
        self.__request = self.__prepare_request()
        response = requests.request(
            method=self.__method, 
            url=self.__request["url"],
            params=self.__request["query_params"], 
            headers=self.__request["headers"],
            json=self.__request["body"]
        )
        self.__response = {
            "body": '' if response.text == '' else response.json(),
            "status_code": response.status_code,
            "headers": response.headers,
            "response_time": response.elapsed.total_seconds(),
        }

        # check response
        ret, validation_results = self.__validate_response()
        overall_success = overall_success and ret

        # post operations
        ret, post_operation_results = self.__run_operations(self.__post_operations)
        overall_success = overall_success and ret

        self.__success = overall_success
        self.__results = pre_operation_results + validation_results + post_operation_results
        # return overall_success, pre_operation_results, validation_results, post_operation_results

    # run operations, return success and messages
    def __run_operations(self, operations: List[Operation]) -> Tuple[bool, List[Tuple[bool, str]]]:
        results = [operation.run(self.__src_object) for operation in operations]
        ret = not len([0 for success, _ in results if not success]) > 0
        return ret, results

    # validate response, return success and messages
    def __validate_response(self) -> Tuple[bool, List[Tuple[bool, str]]]:
        results = []

        if (self.__response is None):
            results.append((False, '无法获取响应'))

        if self.__response["status_code"] != self.__expected_status_code:
            results.append((False, f"预期状态码: {self.__expected_status_code}, 实际状态码: {self.__response['status_code']}"))

        try:
            path = self.__path
            method = self.__method
            code = self.__expected_status_code
            content_type = self.__response["headers"]['Content-Type'].split(';')[0]
            content = swagger_json["paths"][path][method]['responses'][str(code)]['content'][content_type]
        except Exception:
            if self.__response["status_code"] == 204:
                results.append((True, '返回数据结构与接口定义一致'))
            else:
                results.append((False, '接口定义中没有找到返回数据的定义'))
            ret = not len([0 for success, _ in results if not success]) > 0
            return ret, results

        if 'schema' in content:
            schema = pydash.merge(content['schema'], {"components": swagger_json["components"]})
            validator = Draft202012Validator(schema)
        else:
            raise Exception('Not implemented')
        
        ret = True
        for error in sorted(validator.iter_errors(self.__response["body"]), key=str):
            results.append((False, f'返回数据结构与接口定义不一致{error.json_path}: {error.message}'))
            ret = False
        if ret:
            results.append((True, '返回数据结构与接口定义一致'))
            
        ret = not len([0 for success, _ in results if not success]) > 0
        return ret, results

    # prepare request, return request object
    def __prepare_request(self):
        try:
            path_params = json.loads(custom_replace(self.__path_params_str, self.__src_object))
            query_params = json.loads(custom_replace(self.__query_params_str, self.__src_object))
            headers = pydash.merge(
                { "Authorization" : f"Bearer {get_global_variables('access_token')}" },
                json.loads(custom_replace(self.__headers_str, self.__src_object))
            )
            body = json.loads(custom_replace(self.__body_str, self.__src_object))
            path = self.__path
            for key, value in path_params.items():
                path = path.replace('{' + key + '}', custom_replace(str(value), self.__src_object))
            url = self.__url_prefix + path

            return {
                "url": url,
                "path_params": path_params,
                "query_params": query_params,
                "headers": headers,
                "body": body,
            }
        except Exception as e:
            raise Exception(f"请求参数解析失败: {e}")

    def html_body(self):
        def gen_checklist(ret, msg):
            svg_name = 'success' if ret else 'failed'
            return f'<p><img src="../../svgs/{svg_name}.svg" width="20" height="20" /> {msg}</p>'

        return f'''
            <h2>{self.__name}</h2>
            {''.join([gen_checklist(ret, msg) for ret, msg in self.__results])}

            <!-- Tab buttons -->
            <div class="tab">
                <button class="tab-links" onclick="openTab(event, 'Response')" id="defaultOpen">
                    Response
                </button>
                <button class="tab-links" onclick="openTab(event, 'Request')">
                    Request
                </button>
            </div>

            <!-- Tab content -->
            <div id="Response" class="tab-content">

                <p>Status Code: {self.__response['status_code']}</p>
                <p>Response Time: {self.__response['response_time']}s</p>
                
                <h3>Body</h3>
                <pre>{json.dumps(self.__response["body"], indent=4)}</pre>

                <h3>Headers</h3>
                <table>
                    {
                        "".join([f'<tr><td>{key}</td><td>{value}</td></tr>' for key, value in self.__response["headers"].items()])
                    }
                </table>
            </div>

            <div id="Request" class="tab-content">
                <pre>{self.__method.upper()} {self.__request["url"]}</pre>
                <h3>Body</h3>
                <pre>{json.dumps(self.__request["body"], indent=4)}</pre>
                <h3>Headers</h3>
                <table>
                    {
                        "".join([f'<tr><td>{key}</td><td>{value}</td></tr>' for key, value in self.__request["headers"].items()])
                    }
                </table>
            </div>
            <br />
            <script>
                document.getElementById("defaultOpen").click();
            </script>
        '''
