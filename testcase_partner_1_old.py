from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable, AssertEqual
import json

#
# 创建order时会自动创建partner
#

t = Testcase("创建order时会自动创建partner")


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

# 创建order
order = """{
    "type": 0,
    "partner": {
        "name": "name#1",
        "address": "address#1"
    },
    "date": "2024-05-20",
    "invoiceItems": [
        {
            "product": {
                "material": "material#1",
                "name": "name#1",
                "spec": "spec#1",
                "unit": "unit#1",
                "quantity": 0
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "weight": 50,
            "remark": "remark#1",
            "delivered": true
        },
        {
            "product": {
                "material": "material#2",
                "name": "name#2",
                "spec": "spec#2",
                "unit": "unit#2",
                "quantity": 0
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "weight": null,
            "remark": "remark#2",
            "delivered": true
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 2,
    "order": null
}"""
create_order = Step("post", "/invoices", "创建order", body=order)
t.add_step(create_order)  # 2

# 查询单个partner
get_partner = Step(
    "get",
    "/partners/{id}",
    "查询单个partner",
    path_params='{ "id": {{2.response.body.partner.id}} }',
)
t.add_step(get_partner)  # 3

# 查询所有partner
get_partners = Step("get", "/partners", "查询所有partner")
t.add_step(get_partners)  # 4

# 删除user
delete_user = Step(
    "delete", "/users/{id}", "删除user", path_params='{ "id": {{1.response.body.id}} }'
)
t.add_step(delete_user)  # 5

t.run()
