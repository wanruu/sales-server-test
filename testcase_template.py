from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable, AssertEqual
import json

#
#
#

t = Testcase("测试用例名称")
t.description = "测试用例描述"

# 创建user
user = json.dumps({"name": "Hermione", "password": "Ss345678"})
step__create_user = Step("post", "/users", "创建user", body=user)
t.add_step(step__create_user)  # 0

# 登录
step__login = Step("post", "/users/login", "登录", body=user, expected_status_code=200)
step__login.add_post_operation(
    SetGlobalVariable("access_token", "{{1.response.body.accessToken}}")
)
t.add_step(step__login)  # 1

# 删除user
step__delete_user = Step(
    "delete", "/users/{id}", "删除user", path_params='{ "id": {{1.response.body.id}} }'
)
t.add_step(step__delete_user)

t.run()
