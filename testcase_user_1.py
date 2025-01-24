from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable, AssertEqual
import json

#
# 成功创建user并登录修改
#

t = Testcase("成功创建user并登录修改")
t.description = "测试用户创建、登录、修改、查询、删除功能"

# 创建user
user = json.dumps({"name": "Hermione", "password": "12345678"})
create_user = Step("post", "/users", "创建user", body=user)
t.add_step(create_user)  # 0

# 登录
login_user = Step("post", "/users/login", "登录", body=user, expected_status_code=200)
login_user.add_post_operation(
    SetGlobalVariable("access_token", "{{1.response.body.accessToken}}")
)
t.add_step(login_user)  # 1

# 查询user，验证name与创建时一致
find_user = Step(
    "get",
    "/users/{id}",
    "查询user，验证name与创建时一致",
    path_params='{ "id": {{1.response.body.id}} }',
)
find_user.add_post_operation(
    AssertEqual("2.response.body.name", "{{0.request.body.name}}")
)
t.add_step(find_user)  # 2

# 修改user，验证name与修改后一致
new_user = json.dumps({"name": "Hermione2", "password": "123456789"})
modify_user = Step(
    "patch",
    "/users/{id}",
    "修改user，验证name与修改后一致",
    path_params='{ "id": {{1.response.body.id}} }',
    body=new_user,
)
modify_user.add_post_operation(
    AssertEqual("3.response.body.name", "{{3.request.body.name}}")
)
t.add_step(modify_user)  # 3

# 查询user，验证name已修改
find_user = Step(
    "get",
    "/users/{id}",
    "查询user，验证name已修改",
    path_params='{ "id": {{1.response.body.id}} }',
)
find_user.add_post_operation(
    AssertEqual("4.response.body.name", "{{3.request.body.name}}")
)
t.add_step(find_user)  # 4

# 用原本账号login失败
login_user = Step(
    "post", "/users/login", "用原本账号login失败", body=user, expected_status_code=401
)
t.add_step(login_user)  # 5

# 用新账号login成功
login_user = Step(
    "post", "/users/login", "用新账号login成功", body=new_user, expected_status_code=200
)
t.add_step(login_user)  # 6

# 删除user
delete_user = Step(
    "delete",
    "/users/{id}",
    "删除user",
    path_params='{ "id": {{1.response.body.id}} }',
)
t.add_step(delete_user)  # 7

t.run()
