import requests as r
import pydash

js_2_py_type = {
    "object": [dict],
    "oneOf": [dict],
    "array": [list],
    "string": [str],
    "number": [float, int],
    "boolean": [bool]
}

py_2_js_type = {
    "dict": "object",
    "list": "array",
    "str": "string",
    "float": "number",
    "int": "number",
    "bool": "boolean",
    "NoneType": "null"
}

class Swagger:
    def __init__(self, swagger_url):
        json = r.get(swagger_url).json()
        self.__paths = json["paths"]
        self.__schemas = json["components"]["schemas"]

        self.__parsed_responses = {}
        for path, path_obj in self.__paths.items():
            self.__parsed_responses[path] = {}
            for method, method_obj in path_obj.items():
                self.__parsed_responses[path][method] = {}
                for status_code, status_obj in method_obj["responses"].items():
                    self.__parsed_responses[path][method][status_code] = {}
                    for content_type, content_obj in status_obj["content"].items():
                        # if path == '/users' and method == 'post' and status_code == '409' and content_type == 'application/json':
                        schema = {}
                        if "schema" in content_obj:
                            schema = self.parse_schema(content_obj["schema"])
                        self.__parsed_responses[path][method][status_code][content_type] = schema

    @property
    def paths(self):
        return self.__paths

    @property
    def schemas(self):
        return self.__schemas

    def parse_schema(self, raw):
        base = {"type": raw["type"] if "type" in raw else "object"}
        if "oneOf" in raw and "type" not in raw:
            base["type"] = "oneOf"
        if "nullable" in raw:
            base["nullable"] = raw["nullable"]

        if "properties" in raw:
            properties = {}
            for key, value in raw["properties"].items():
                properties[key] = self.parse_schema(value)
            return pydash.set_(base, "properties", properties)

        if "$ref" in raw:
            sub_schema = self.parse_schema(self.__schemas.get(raw["$ref"].split("/")[-1]))
            return pydash.merge(base, sub_schema)

        if "allOf" in raw:
            aggregated = {}
            for item in raw["allOf"]:
                aggregated = pydash.merge(aggregated, self.parse_schema(item))
            if base["type"] == "array":
                return pydash.set_(base, "items", aggregated)
            return pydash.merge(base, aggregated)
    
        if base["type"] == "array":
            return pydash.set_(base, "items", self.parse_schema(raw["items"]))

        if "oneOf" in raw:
            arr = []
            for item in raw["oneOf"]:
                arr.append(self.parse_schema(item))
            return pydash.set_(base, "items", arr)

        return raw

    def iter_check(self, schema, instance, path=[]):
        if "nullable" in schema and schema["nullable"] and instance is None:
            return True
        
        if schema["type"] == "oneOf":
            ret = False
            for item in schema["items"]:
                sub_ret = self.iter_check(item, instance, path)
                if sub_ret:
                    ret = True
                    break
            return ret

        if type(instance) not in js_2_py_type[schema["type"]]:
            self.__messages.append(f'{".".join(path)}: Expected {schema["type"]}, but got {py_2_js_type[type(instance).__name__]}')
            return False
        
        if "enum" in schema and schema["enum"] and instance not in schema["enum"]:
            self.__messages.append(f'{".".join(path)}: Expected one of [{", ".join(schema["enum"])}], but got {instance}')
            return False

        if schema["type"] in ["number", "string", "boolean"]:
            return True
        
        if schema["type"] == "object":
            ret = True
            for key, value in schema["properties"].items():
                sub_ret = self.iter_check(value, instance[key] if key in instance else None, path + [key])
                if not sub_ret:
                    ret = False
            return ret
        
        if schema["type"] == "array":
            ret = True
            for i, item in enumerate(instance):
                sub_ret = self.iter_check(schema["items"], item, path + [i])
                if not sub_ret:
                    ret = False
            return ret
        
        raise Exception("unknown type")

    def check_response(self, path, method, status_code, content_type, response):
        schema = self.__parsed_responses[path][method][status_code][content_type]
        schema = self.parse_schema(schema)
        self.__messages = []
        return self.iter_check(schema, response), self.__messages
