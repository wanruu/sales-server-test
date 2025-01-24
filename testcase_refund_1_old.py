from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable, AssertEqual
import json

#
# 创建refund
#
# - 创建refund时，不可以新增`product`。
# - 创建refund时，必须指定`invoiceItems.orderItem`，否则报`400`。如果对应`orderItem`不存在，报`404`。
#

t = Testcase("创建refund")
t.description = """- 创建refund时，不可以新增`product`。
- 创建refund时，必须指定`invoiceItems.orderItem`，否则报`400`。如果对应`orderItem`不存在，报`404`。
"""

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
order = json.dumps(
    {
        "type": 0,
        "partner": {"name": "partner#1"},
        "date": "2025-10-12",
        "invoiceItems": [
            {
                "product": {
                    "material": "material#1",
                    "name": "name#1",
                    "spec": "spec#1",
                    "unit": "unit#1",
                },
                "price": 100,
                "quantity": 2,
                "originalAmount": 200,
                "discount": 80,
                "amount": 160,
                "remark": "remark#1",
                "delivered": False,
                "orderItem": {"id": 1},
            },
            {
                "product": {
                    "material": "material#2",
                    "name": "name#2",
                    "spec": "spec#2",
                    "unit": "unit#2",
                },
                "price": 100,
                "quantity": 2,
                "originalAmount": 200,
                "discount": 80,
                "amount": 160,
                "weight": 50,
                "remark": "remark#2",
                "delivered": False,
                "orderItem": None,
            },
        ],
        "amount": 1000,
        "prepayment": 50,
        "payment": 200,
        "delivered": 0,
        "order": None,
    }
)
create_order = Step("post", "/invoices", "创建order", body=order)
t.add_step(create_order)  # 2

# 创建refund，product id不可以为空
refund = """{
    "type": 2,
    "partner": { "id": {{2.response.body.partner.id}} },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
                "material": "material#1",
                "name": "name#1",
                "spec": "spec#1",
                "unit": "unit#1"
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "remark": "remark#1",
            "delivered": false,
            "orderItem":{ "id": {{2.response.body.invoiceItems.0.id}} }
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": {{2.response.body.id}} }
}"""
create_refund_1 = Step(
    "post",
    "/invoices",
    "创建refund，product id不可以为空",
    body=refund,
    expected_status_code=400,
)
t.add_step(create_refund_1)  # 3

# 创建refund，orderItem不可以为空
refund = """{
    "type": 2,
    "partner": { "id": {{2.response.body.partner.id}} },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": { "id": {{2.response.body.invoiceItems.0.product.id}} },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "remark": "remark#1",
            "delivered": false
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": {{2.response.body.id}} }
}"""
create_refund_2 = Step(
    "post",
    "/invoices",
    "创建refund，orderItem不可以为空",
    body=refund,
    expected_status_code=400,
)
t.add_step(create_refund_2)  # 4

# 创建refund，orderItem id不可以为null
refund = """{
    "type": 2,
    "partner": {
        "id": {{2.response.body.partner.id}}
    },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
              "id": {{2.response.body.invoiceItems.0.product.id}}
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "remark": "remark#1",
            "delivered": false,
            "orderItem": {
                "id": null
            }
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": {{2.response.body.id}} }
}"""
create_refund_3 = Step(
    "post",
    "/invoices",
    "创建refund，orderItem id不可以为null",
    body=refund,
    expected_status_code=400,
)
t.add_step(create_refund_3)  # 5

# 创建refund，orderItem id不可以为不存在的值
refund = """{
    "type": 2,
    "partner": {
        "id": {{2.response.body.partner.id}}
    },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
              "id": {{2.response.body.invoiceItems.0.product.id}}
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "remark": "remark#1",
            "delivered": false,
            "orderItem": {
                "id": 1
            }
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": {{2.response.body.id}} }
}"""
create_refund_4 = Step(
    "post",
    "/invoices",
    "创建refund，orderItem id不可以为不存在的值",
    body=refund,
    expected_status_code=404,
)
t.add_step(create_refund_4)  # 6

# 创建refund
refund = """{
    "type": 2,
    "partner": {
        "id": {{2.response.body.partner.id}}
    },
    "date": "{{2.request.body.date}}",
    "invoiceItems": [
        {
            "product": {
              "id": {{2.response.body.invoiceItems.0.product.id}}
            },
            "price": 1000,
            "quantity": 20,
            "originalAmount": 2000,
            "discount": 100,
            "amount": 1600,
            "remark": "remark#refund#1",
            "delivered": true,
            "orderItem": {
                "id": {{2.response.body.invoiceItems.0.id}}
            }
        }
    ],
    "amount": 423,
    "prepayment": 432,
    "payment": 34,
    "delivered": 1,
    "order": { "id": {{2.response.body.id}} }
}"""
create_refund_5 = Step("post", "/invoices", "创建refund", body=refund)
create_refund_5.add_post_operation(
    AssertEqual(
        "7.response.body.invoiceItems.0.product.id",
        "{{2.response.body.invoiceItems.0.product.id}}",
    )
)
create_refund_5.add_post_operation(
    AssertEqual(
        "7.response.body.invoiceItems.0.orderItem.id",
        "{{2.response.body.invoiceItems.0.id}}",
    )
)
create_refund_5.add_post_operation(
    AssertEqual("7.response.body.partner.id", "{{2.response.body.partner.id}}")
)
create_refund_5.add_post_operation(
    AssertEqual("7.response.body.order.id", "{{2.response.body.id}}")
)
t.add_step(create_refund_5)  # 7

# 查询单个refund
query_refund = Step(
    "get",
    "/invoices/{id}",
    "查询单个refund",
    path_params='{"id": {{7.response.body.id}}}',
)
query_refund.add_post_operation(
    AssertEqual(
        "8.response.body.number",
        "{{7.request.body.date.substr(0,4)}}{{7.request.body.date.substr(5,7)}}{{7.request.body.date.substr(8,10)}}0001",
    )
)
query_refund.add_post_operation(
    AssertEqual("8.response.body.partner.name", "{{2.request.body.partner.name}}")
)
t.add_step(query_refund)  # 8

# 查询单个order
query_order = Step(
    "get",
    "/invoices/{id}",
    "查询单个order",
    path_params='{"id": {{2.response.body.id}}}',
)
query_order.add_post_operation(
    AssertEqual(
        "9.response.body.number",
        "{{2.request.body.date.substr(0,4)}}{{2.request.body.date.substr(5,7)}}{{2.request.body.date.substr(8,10)}}0001",
    )
)
t.add_step(query_order)  # 9

# 删除user
delete_user = Step(
    "delete",
    "/users/{id}",
    "删除user",
    path_params='{"id": {{1.response.body.id}} }',
)
t.add_step(delete_user)  # 10

t.run()
