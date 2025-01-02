
from api_step import ApiStep
import pydash

# variables
global_variables = {}
def set_global_variables(path, value):
    global global_variables
    global_variables = pydash.set_(global_variables, path, value)
def get_global_variables(path):
    global global_variables
    return pydash.get(global_variables, path)



step = ApiStep('post', '/users/login', body={'name': 'hello world', 'password': '12345678'}, code=200)
step.add_process('post', lambda step: set_global_variables("access_token", step.get_variable('response.body.data.accessToken')))
step.run()

ApiStep.update_headers({ "Authorization": "Bearer " + get_global_variables("access_token") })



# 成功创建user并登录修改
# user = {
#     "name": "Hermione",
#     "password": "12345678"
# }
# create_user = ApiStep('post', '/users', body=user)
# create_user.expect(201)
# create_user.run()