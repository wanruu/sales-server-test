from lib.step import Step
from lib.utils import custom_get
from lib.operation import SetGlobalVariableOperation
import json

#
# 用户名不可以重复
#

# 创建user1
user_1 = '{"name": "Hermione", "password": "12345678"}'
create_user_1 = Step('post', '/users', '创建user1', body=user_1)
create_user_1.run()

# 创建user2，因name重复而失败
create_user_2 = Step('post', '/users', '创建user2，因name重复而失败', body=user_1, expected_status_code=409)
create_user_2.run()

# 创建user2
user_2 = '{"name": "Hermione2", "password": "123456789"}'
create_user_2 = Step('post', '/users', '创建user2', body=user_2)
create_user_2.run()

# 登录user1
login_user_1 = Step('post', '/users/login', '登录user1', body=user_1, expected_status_code=200)
login_user_1.add_post_operation(SetGlobalVariableOperation("access_token", "{{response.body.data.accessToken}}"))
login_user_1.run()
user_1_id = custom_get(login_user_1, 'response.body.data.id')

# 修改user1为user2的name，失败
user_1_update = '{"name": "Hermione2", "password": "12345678"}'
update_user_1 = Step('patch', '/users/{id}', '修改user1为user2的name，失败', body=user_1_update, path_params=json.dumps({"id": str(user_1_id)}), expected_status_code=409)
update_user_1.run()

# 删除user1
delete_user_1 = Step('delete', '/users/{id}', '删除user1', path_params=json.dumps({"id": user_1_id}))
delete_user_1.run()

# 登录user2
login_user_2 = Step('post', '/users/login', '登录user2', body=user_2, expected_status_code=200)
login_user_2.add_post_operation(SetGlobalVariableOperation("access_token", "{{response.body.data.accessToken}}"))
login_user_2.run()
user_2_id = custom_get(login_user_2, 'response.body.data.id')

# 删除user2
delete_user_2 = Step('delete', '/users/{id}', '删除user2', path_params=json.dumps({"id": user_2_id}))
delete_user_2.run()