from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable
import json
import data

#
# 类型测试 - request - partner
#

t = Testcase("类型测试 - request - partner")
t.description = ""


# 创建user
user_str = json.dumps(data.accepted_user)
step__create_user = Step("post", "/users", "创建user", body=user_str)
t.add_step(step__create_user)  # 0

# 登录
step__login = Step(
    "post", "/users/login", "登录", body=user_str, expected_status_code=200
)
step__login.add_post_operation(
    SetGlobalVariable("access_token", "{{1.response.body.accessToken}}")
)
t.add_step(step__login)  # 1

# 创建partner
for partner in data.accepted_partners:
    partner_str = json.dumps(partner)
    step__create_partner = Step("post", "/partners", "创建partner", body=partner_str)
    t.add_step(step__create_partner)

# 创建partner
for partner in data.unaccepted_partners:
    partner_str = json.dumps(partner)
    step__create_partner = Step(
        "post", "/partners", "创建partner", body=partner_str, expected_status_code=400
    )
    t.add_step(step__create_partner)

# 删除user
step__delete_user = Step(
    "delete", "/users/{id}", "删除user", path_params='{ "id": {{1.response.body.id}} }'
)
t.add_step(step__delete_user)


t.run()
