from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariableOperation, AssertEqualOperation
import json

#
# 
#

t = Testcase('测试用例名称', '测试用例描述')

# 创建user
user = json.dumps({"name": "Hermione", "password": "12345678"})
create_user = Step('post', '/users', '创建user', body=user)
t.add_step(create_user) #0

# 登录
login_user = Step('post', '/users/login', '登录', body=user, expected_status_code=200)
login_user.add_post_operation(SetGlobalVariableOperation('access_token', '{{1.response.body.data.accessToken}}'))
t.add_step(login_user) #1

# 删除user
delete_user = Step('delete', '/users/{id}', '删除user', path_params='{ "id": {{1.response.body.data.id}} }')
t.add_step(delete_user) #2

t.run()

