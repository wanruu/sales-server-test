from lib.step import Step
from lib.utils import custom_get
from lib.operation import SetGlobalVariableOperation
import json

#
# 不可查看、修改或删除其他user的信息
#

# 创建user1
user_1 = '{"name": "Hermione", "password": "12345678"}'
create_user_1 = Step('post', '/users', '创建user1', body=user_1)
create_user_1.run()
user_1_id = custom_get(create_user_1, 'response.body.data.id')

# 创建user2
user_2 = '{"name": "Hermione2", "password": "123456789"}'
create_user_2 = Step('post', '/users', '创建user2', body=user_2)
create_user_2.run()
user_2_id = custom_get(create_user_2, 'response.body.data.id')

# 查询user1，401
query_user_1 = Step('get', '/users/{id}', '查询user1，401', path_params=json.dumps({ "id": user_1_id }), expected_status_code=401)
query_user_1.run()

# 登录user1
login_user_1 = Step('post', '/users/login', '登录user1', body=user_1, expected_status_code=200)
login_user_1.add_post_operation(SetGlobalVariableOperation("access_token", "{{response.body.data.accessToken}}"))
login_user_1.run()

# 查询user2，401
query_user_2 = Step('get', '/users/{id}', '查询user2，401', path_params=json.dumps({ "id": user_2_id }), expected_status_code=401)
query_user_2.run()

# 修改user2，401
user_2_update = '{"name": "Hermione", "password": "12345678"}'
update_user_2 = Step('patch', '/users/{id}', '修改user2，401', path_params=json.dumps({ "id": user_2_id }), body=user_2_update, expected_status_code=401)
update_user_2.run()

# 删除user1
delete_user_1 = Step('delete', '/users/{id}', '删除user1', path_params=json.dumps({ "id": user_1_id }))
delete_user_1.run()

# 登录user2
login_user_2 = Step('post', '/users/login', '登录user2', body=user_2, expected_status_code=200)
login_user_2.add_post_operation(SetGlobalVariableOperation("access_token", "{{response.body.data.accessToken}}"))
login_user_2.run()

# 删除user2
delete_user_2 = Step('delete', '/users/{id}', '删除user2',path_params=json.dumps({ "id": user_2_id }))
delete_user_2.run()