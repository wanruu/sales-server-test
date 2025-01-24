from lib.step import Step
from lib.testcase import Testcase
import json
import data

#
# 类型测试 - request - user
#

t = Testcase("类型测试 - request - user")
t.description = ""


for user in data.unaccepted_users:
    # 创建user
    user_str = json.dumps(user)
    create_user = Step(
        "post", "/users", "创建user", body=user_str, expected_status_code=400
    )
    t.add_step(create_user)

t.run()
