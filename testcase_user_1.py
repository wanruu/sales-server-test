from lib.step import Step
from lib.utils import custom_get
from lib.operation import SetGlobalVariableOperation, AssertEqualOperation
import json

#
# 成功创建user并登录修改
#

# 创建user
user = '{"name": "Hermione", "password": "12345678"}'
create_user = Step('post', '/users', '创建user', body=user)
create_user.run()

# 登录
login_user = Step('post', '/users/login', '登录', body=user, expected_status_code=200)
login_user.add_post_operation(SetGlobalVariableOperation('access_token', '{{response.body.data.accessToken}}'))
login_user.run()
login_user_id = custom_get(login_user, 'response.body.data.id')

# 查询user，验证name与创建时一致
find_user = Step('get', '/users/{id}', '查询user，验证name与创建时一致', path_params=json.dumps({ "id": login_user_id }))
find_user.add_post_operation(AssertEqualOperation('response.body.data.name', custom_get(create_user, 'request.body.name')))
find_user.run()

# 修改user，验证name与修改后一致
new_user = '{"name": "Hermione2", "password": "123456789"}'
modify_user = Step('patch', '/users/{id}', '修改user，验证name与修改后一致', path_params=json.dumps({ "id": login_user_id }), body=new_user)
modify_user.add_post_operation(AssertEqualOperation('response.body.data.name', '{{request.body.name}}'))
modify_user.run()

# 查询user，验证name已修改
find_user = Step('get', '/users/{id}', '查询user，验证name已修改', path_params=json.dumps({ "id": login_user_id }))
modify_user.add_post_operation(AssertEqualOperation('response.body.data.name', custom_get(modify_user, 'request.body.name')))
find_user.run()

# 用原本账号login失败
login_user = Step('post', '/users/login', '用原本账号login失败', body=user, expected_status_code=401)
login_user.run()

# 用新账号login成功
login_user = Step('post', '/users/login', '用新账号login成功', body=new_user, expected_status_code=200)
login_user.run()

# 删除user
delete_user = Step('delete', '/users/{id}', '删除user', path_params=json.dumps({ "id": login_user_id }))
delete_user.run()