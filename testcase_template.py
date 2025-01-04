from lib.step import Step
from lib.utils import custom_get
from lib.operation import SetGlobalVariableOperation, AssertEqualOperation
import json

#
# 
#

# 创建user
user = json.dumps({"name": "Hermione", "password": "12345678"})
create_user = Step('post', '/users', '创建user', body=user)
create_user.run()

# 登录
login_user = Step('post', '/users/login', '登录', body=user, expected_status_code=200)
login_user.add_post_operation(SetGlobalVariableOperation('access_token', '{{response.body.data.accessToken}}'))
login_user.run()
login_user_id = custom_get(login_user, 'response.body.data.id')

# 删除user
delete_user = Step('delete', '/users/{id}', '删除user', path_params=json.dumps({ "id": login_user_id }))
delete_user.run()