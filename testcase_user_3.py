from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariableOperation
import json

#
# 用户名不可以重复
#

t = Testcase("用户名不可以重复")

# 创建user1
user_1 = json.dumps({"name": "Hermione", "password": "12345678"})
create_user_1 = Step("post", "/users", "创建user1", body=user_1)
t.add_step(create_user_1)  # 0

# 创建user2，因name重复而失败
create_user_2 = Step(
    "post",
    "/users",
    "创建user2，因name重复而失败",
    body=user_1,
    expected_status_code=409,
)
t.add_step(create_user_2)  # 1

# 创建user2
user_2 = json.dumps({"name": "Hermione2", "password": "123456789"})
create_user_2 = Step("post", "/users", "创建user2", body=user_2)
t.add_step(create_user_2)  # 2

# 登录user1
login_user_1 = Step(
    "post", "/users/login", "登录user1", body=user_1, expected_status_code=200
)
login_user_1.add_post_operation(
    SetGlobalVariableOperation("access_token", "{{3.response.body.accessToken}}")
)
t.add_step(login_user_1)  # 3

# 修改user1为user2的name，失败
user_1_update = json.dumps({"name": "Hermione2", "password": "12345678"})
update_user_1 = Step(
    "patch",
    "/users/{id}",
    "修改user1为user2的name，失败",
    body=user_1_update,
    path_params='{ "id": {{3.response.body.id}} }',
    expected_status_code=409,
)
t.add_step(update_user_1)  # 4

# 删除user1
delete_user_1 = Step(
    "delete",
    "/users/{id}",
    "删除user1",
    path_params='{ "id": {{3.response.body.id}} }',
)
t.add_step(delete_user_1)  # 5

# 登录user2
login_user_2 = Step(
    "post", "/users/login", "登录user2", body=user_2, expected_status_code=200
)
login_user_2.add_post_operation(
    SetGlobalVariableOperation("access_token", "{{6.response.body.accessToken}}")
)
t.add_step(login_user_2)  # 6

# 删除user2
delete_user_2 = Step(
    "delete",
    "/users/{id}",
    "删除user2",
    path_params='{ "id": {{6.response.body.id}} }',
)
t.add_step(delete_user_2)  # 7

t.run()
