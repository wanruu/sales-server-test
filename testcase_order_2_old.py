from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable, AssertEqual
import json


#
# 创建order，同时创建partner和部分product
#
# - 创建order时，`order`可以为`null`或不包含，保存时只会是`null`。【这里测试的是`null`】
#

t = Testcase("创建order，同时创建partner和部分product")
t.description = """- 创建order时，`order`可以为`null`或不包含，保存时只会是`null`。【这里测试的是`null`】"""

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

# 创建product
product = json.dumps(
    {
        "material": "material#1",
        "name": "name#1",
        "spec": "spec#1",
        "unit": "unit#1",
        "quantity": 10,
    }
)
create_product = Step("post", "/products", "创建product", body=product)
t.add_step(create_product)  # 2

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
                "id": {{2.response.body.id}}
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
t.add_step(create_order)  # 3

# 查询单个partner
get_partner = Step(
    "get",
    "/partners/{id}",
    "查询单个partner",
    path_params='{"id": {{3.response.body.partner.id}}}',
)
get_partner.add_post_operation(
    AssertEqual("4.response.body.name", "{{3.request.body.partner.name}}")
)
get_partner.add_post_operation(
    AssertEqual("4.response.body.address", "{{3.request.body.partner.address}}")
)
get_partner.add_post_operation(AssertEqual("4.response.body.folder", ""))
get_partner.add_post_operation(AssertEqual("4.response.body.phone", ""))
t.add_step(get_partner)  # 4

# 查询单个order
get_order = Step(
    "get",
    "/invoices/{id}",
    "查询单个order",
    path_params='{"id": {{3.response.body.id}}}',
)
get_order.add_post_operation(
    AssertEqual("5.response.body.partner", "{{4.response.body}}")
)
t.add_step(get_order)  # 5

# 查询所有product
get_all_product = Step("get", "/products", "查询所有product")
get_all_product.add_post_operation(AssertEqual("6.response.body.data.length", 2))
t.add_step(get_all_product)  # 6

# 查询所有invoice
get_all_invoice = Step("get", "/invoices", "查询所有invoice")
get_all_invoice.add_post_operation(AssertEqual("7.response.body.data.length", 1))
t.add_step(get_all_invoice)  # 7

# 删除user
delete_user = Step(
    "delete",
    "/users/{id}",
    "删除user",
    path_params='{ "id": {{1.response.body.id}} }',
)
t.add_step(delete_user)  # 8

t.run()
