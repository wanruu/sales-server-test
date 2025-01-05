import requests
import pydash
from jsonschema import Draft202012Validator
from lib.utils import get_global_variables, custom_replace
from typing import Tuple, List, Literal
import json
from lib.operation import Operation


_DEFAULT_STATUS_CODE_DICT = {
    "delete": 204,
    "get": 200,
    "post": 201,
    "put": 200,
    "patch": 200,
}
_URL_PREFIX = "http://localhost:3000"
swagger = requests.get(f"{_URL_PREFIX}/api-doc-json").json()

# type
HttpMethod = Literal["delete", "get", "post", "put", "patch"]
Log = Tuple[bool, str]


class Step:
    def __init__(
        self,
        method: HttpMethod,
        path: str,
        name: str = None,
        path_params: str = "{}",
        query_params: str = "{}",
        headers: str = "{}",
        body: str = "{}",
        expected_status_code=None,
    ):
        self.__name = name
        self.__method = method
        self.__path = path
        self.__headers_str = headers
        self.__body_str = body
        self.__path_params_str = path_params
        self.__query_params_str = query_params
        if expected_status_code is None:
            expected_status_code = _DEFAULT_STATUS_CODE_DICT.get(method)
        self.__expected_status_code = int(expected_status_code)
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

    @property
    def results(self):
        return self.__results

    def add_pre_operation(self, operation: Operation):
        self.__pre_operations.append(operation)

    def add_post_operation(self, operation: Operation):
        self.__post_operations.append(operation)

    # run step, set self.__response, self.__request, self.__success, self.__results
    def run(self):
        self.__success = True
        self.__results = []

        # pre operations
        ret, pre_operation_results = self.__run_operations(self.__pre_operations)
        pre_operation_results = [
            (ret, f"前置操作: {msg}") for ret, msg in pre_operation_results
        ]
        self.__success = self.__success and ret
        self.__results += pre_operation_results

        # send api
        self.__request = self.__prepare_request()
        response = requests.request(
            method=self.__method,
            url=self.__request["url"],
            params=self.__request["query_params"],
            headers=self.__request["headers"],
            json=self.__request["body"],
        )
        self.__response = {
            "body": "" if response.text == "" else response.json(),
            "status_code": response.status_code,
            "headers": response.headers,
            "response_time": response.elapsed.total_seconds(),
        }

        # check response
        ret, validation_results = self.__validate_response()
        self.__success = self.__success and ret
        self.__results += validation_results

        # post operations
        ret, post_operation_results = self.__run_operations(self.__post_operations)
        post_operation_results = [
            (ret, f"后置操作: {msg}") for ret, msg in post_operation_results
        ]
        self.__success = self.__success and ret
        self.__results += post_operation_results

    # run operations, return success and messages
    def __run_operations(self, operations: List[Operation]) -> Tuple[bool, List[Log]]:
        results = [operation.run(self.__src_object) for operation in operations]
        error = len([0 for success, _ in results if not success]) > 0
        return not error, results

    # validate response, return success and messages
    def __validate_response(self) -> Tuple[bool, List[Log]]:
        results = []

        # check if response exists
        if self.__response is None:
            results.append((False, "无法获取响应"))

        # check status code
        expected = self.__expected_status_code
        actual = self.__response["status_code"]
        if actual != expected:
            msg = f"预期状态码: {expected}, 实际状态码: {actual}"
            results.append((False, msg))

        # check response body
        headers = self.__response["headers"]
        body = self.__response["body"]
        if "Content-Type" not in headers:
            if body == "":
                results.append((True, "返回数据结构与接口定义一致"))
            else:
                results.append((False, "返回数据结构与接口定义不一致"))
        else:
            try:
                # construct validator
                responses = swagger["paths"][self.__path][self.__method]["responses"]
                code = str(self.__expected_status_code)
                content_type = headers["Content-Type"].split(";")[0]
                schema = pydash.merge(
                    responses[code]["content"][content_type]["schema"],
                    {"components": swagger["components"]},
                )
                validator = Draft202012Validator(schema)

                # start validation
                errors = sorted(validator.iter_errors(body), key=str)
                for error in errors:
                    msg = f"返回数据结构与接口定义不一致{error.json_path}: {error.message}"
                    results.append((False, msg))
                if len(errors) == 0:
                    results.append((True, "返回数据结构与接口定义一致"))
            except KeyError:
                results.append((False, "接口定义中没有找到返回数据的定义"))
            except Exception as e:
                results.append((False, f"接口定义解析失败: {e}"))

        ret = not len([0 for success, _ in results if not success]) > 0
        return ret, results

    # prepare request, return request object
    def __prepare_request(self):
        try:
            path_params = json.loads(
                custom_replace(self.__path_params_str, self.__src_object)
            )
            query_params = json.loads(
                custom_replace(self.__query_params_str, self.__src_object)
            )
            headers = pydash.merge(
                {"Authorization": f"Bearer {get_global_variables('access_token')}"},
                json.loads(custom_replace(self.__headers_str, self.__src_object)),
            )
            body = json.loads(custom_replace(self.__body_str, self.__src_object))
            path = self.__path
            for key, value in path_params.items():
                path = path.replace(
                    "{" + key + "}", custom_replace(str(value), self.__src_object)
                )
            url = _URL_PREFIX + path

            return {
                "url": url,
                "path_params": path_params,
                "query_params": query_params,
                "headers": headers,
                "body": body,
            }
        except Exception as e:
            raise Exception(f"请求参数解析失败: {e}")
