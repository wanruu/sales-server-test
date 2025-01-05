from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariableOperation
import json

#
# 不可查看、修改或删除其他user的信息
#

t = Testcase("不可查看、修改或删除其他user的信息")

# 创建user1
user_1 = json.dumps({"name": "Hermione", "password": "12345678"})
create_user_1 = Step("post", "/users", "创建user1", body=user_1)
t.add_step(create_user_1)  # 0

# 创建user2
user_2 = json.dumps({"name": "Hermione2", "password": "123456789"})
create_user_2 = Step("post", "/users", "创建user2", body=user_2)
t.add_step(create_user_2)  # 1

# 查询user1，401
query_user_1 = Step(
    "get",
    "/users/{id}",
    "查询user1，401",
    path_params='{ "id": {{0.response.body.id}} }',
    expected_status_code=401,
)
t.add_step(query_user_1)  # 2

# 登录user1
login_user_1 = Step(
    "post", "/users/login", "登录user1", body=user_1, expected_status_code=200
)
login_user_1.add_post_operation(
    SetGlobalVariableOperation("access_token", "{{3.response.body.accessToken}}")
)
t.add_step(login_user_1)  # 3

# 查询user2，401
query_user_2 = Step(
    "get",
    "/users/{id}",
    "查询user2，401",
    path_params='{ "id": {{1.response.body.id}} }',
    expected_status_code=401,
)
t.add_step(query_user_2)  # 4

# 修改user2，401
user_2_update = json.dumps({"name": "Hermione", "password": "12345678"})
update_user_2 = Step(
    "patch",
    "/users/{id}",
    "修改user2，401",
    path_params='{ "id": {{1.response.body.id}} }',
    body=user_2_update,
    expected_status_code=401,
)
t.add_step(update_user_2)  # 5

# 删除user1
delete_user_1 = Step(
    "delete",
    "/users/{id}",
    "删除user1",
    path_params='{ "id": {{3.response.body.id}} }',
)
t.add_step(delete_user_1)  # 6

# 登录user2
login_user_2 = Step(
    "post", "/users/login", "登录user2", body=user_2, expected_status_code=200
)
login_user_2.add_post_operation(
    SetGlobalVariableOperation("access_token", "{{7.response.body.accessToken}}")
)
t.add_step(login_user_2)  # 7

# 删除user2
delete_user_2 = Step(
    "delete",
    "/users/{id}",
    "删除user2",
    path_params='{ "id": {{7.response.body.id}} }',
)
t.add_step(delete_user_2)  # 8

t.run()
