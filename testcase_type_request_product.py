from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable
import json
import data

#
# 类型测试 - request - product
#

t = Testcase("类型测试 - request - product")
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

# 创建product
for product in data.accepted_products:
    product_str = json.dumps(product)
    step__create_product = Step("post", "/products", "创建product", body=product_str)
    t.add_step(step__create_product)

# 创建product
for product in data.unaccepted_products:
    product_str = json.dumps(product)
    step__create_product = Step(
        "post", "/products", "创建product", body=product_str, expected_status_code=400
    )
    t.add_step(step__create_product)

# 删除user
step__delete_user = Step(
    "delete", "/users/{id}", "删除user", path_params='{ "id": {{1.response.body.id}} }'
)
t.add_step(step__delete_user)


t.run()
