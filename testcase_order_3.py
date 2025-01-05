from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariableOperation, AssertEqualOperation
import json

#
# 更新order
#
# - 更新order时，`type`和`number`不可以更改。
# - 更新order时，可以新增`partner`，但不可以修改原有的`partner`。【这里测试的是新增】
# - 更新order时，不在列表里的`invoiceItem`应该被删除。
# - 更新order时，在列表里的`invoiceItem`如果带`id`，其数据应该更新，`id`不改变，可以新增`product`，但不可以更改原有的`product`。
# - 更新order时，在列表里的`invoiceItem`如果不带`id`，则应该新建。可以新增`product`，但不可以更改原有的`product`。
#

t = Testcase("更新order")
t.description = """- 更新order时，`type`和`number`不可以更改。
- 更新order时，可以新增`partner`，但不可以修改原有的`partner`。【这里测试的是新增】
- 更新order时，不在列表里的`invoiceItem`应该被删除。
- 更新order时，在列表里的`invoiceItem`如果带`id`，其数据应该更新，`id`不改变，可以新增`product`，但不可以更改原有的`product`。
- 更新order时，在列表里的`invoiceItem`如果不带`id`，则应该新建。可以新增`product`，但不可以更改原有的`product`。
"""

# 创建user
user = json.dumps({"name": "Hermione", "password": "12345678"})
create_user = Step("post", "/users", "创建user", body=user)
t.add_step(create_user)  # 0

# 登录
login_user = Step("post", "/users/login", "登录", body=user, expected_status_code=200)
login_user.add_post_operation(
    SetGlobalVariableOperation("access_token", "{{1.response.body.data.accessToken}}")
)
t.add_step(login_user)  # 1

# 创建order
order = json.dumps(
    {
        "type": 0,
        "partner": {"name": "partner#1", "folder": "folder#1"},
        "date": "2024-05-20",
        "invoiceItems": [
            {
                "product": {
                    "material": "material#1",
                    "name": "name#1",
                    "spec": "spec#1",
                    "unit": "unit#1",
                },
                "price": 432,
                "quantity": 432,
                "originalAmount": 567,
                "discount": 80,
                "amount": 25,
                "weight": 643,
                "remark": "remark#1",
                "delivered": True,
            },
            {
                "product": {
                    "material": "material#2",
                    "name": "name#2",
                    "spec": "spec#2",
                    "unit": "unit#2",
                },
                "price": 643,
                "quantity": 24,
                "originalAmount": 654,
                "discount": 100,
                "amount": 52,
                "weight": 525,
                "remark": "remark#2",
                "delivered": True,
            },
            {
                "product": {
                    "material": "material#3",
                    "name": "name#3",
                    "spec": "spec#3",
                    "unit": "unit#3",
                },
                "price": 42,
                "quantity": 425,
                "originalAmount": 12423,
                "discount": 80,
                "amount": 8645,
                "weight": 345,
                "remark": "remark#3",
                "delivered": False,
            },
        ],
        "amount": 1000,
        "prepayment": 50,
        "payment": 200,
        "delivered": 2,
    }
)
create_order = Step("post", "/invoices", "创建order", body=order)
t.add_step(create_order)  # 2

# 更新order
order_update = """{
    "type": 0,
    "partner": { "name": "partner#2", "address": "address#2" },
    "date": "2000-05-20",
    "invoiceItems": [
        {
            "id": {{2.response.body.data.invoiceItems.1.id}},
            "product": {
                "id": {{2.response.body.data.invoiceItems.1.product.id}},
                "name": "shouldn't appear"
            },
            "price": 1,
            "quantity": 1,
            "originalAmount": 1,
            "discount": 1,
            "amount": 1,
            "weight": 1,
            "remark": "1",
            "delivered": false
        },
        {
            "id": {{2.response.body.data.invoiceItems.2.id}},
            "product": {
                "material": "material#4",
                "name": "name#4",
                "spec": "spec#4",
                "unit": "unit#4"
            },
            "price": 2,
            "quantity": 2,
            "originalAmount": 2,
            "discount": 2,
            "amount": 2,
            "remark": "2",
            "delivered": true
        },
        {
            "product": {
                "id": {{2.response.body.data.invoiceItems.0.product.id}}
            },
            "price": 3,
            "quantity": 3,
            "originalAmount": 3,
            "discount": 3,
            "amount": 3,
            "weight": null,
            "remark": "3",
            "delivered": true
        }
    ],
    "amount": 1,
    "prepayment": 1,
    "payment": 1,
    "delivered": 1
}"""
update_order = Step(
    "put",
    "/invoices/{id}",
    "更新order",
    path_params='{"id": {{2.response.body.data.id}}}',
    body=order_update,
)
t.add_step(update_order)  # 3

# 查询单个partner
get_partner = Step(
    "get",
    "/partners/{id}",
    "查询单个partner",
    path_params='{"id": {{2.response.body.data.partner.id}}}',
)
get_partner.add_post_operation(
    AssertEqualOperation("4.response.body.data.name", "{{2.request.body.partner.name}}")
)
get_partner.add_post_operation(
    AssertEqualOperation(
        "4.response.body.data.folder", "{{2.request.body.partner.folder}}"
    )
)
get_partner.add_post_operation(AssertEqualOperation("4.response.body.data.address", ""))
get_partner.add_post_operation(AssertEqualOperation("4.response.body.data.phone", ""))
t.add_step(get_partner)  # 4

# 查询单个order
get_order = Step(
    "get",
    "/invoices/{id}",
    "查询单个order",
    path_params='{"id": {{2.response.body.data.id}}}',
)
get_order.add_post_operation(
    AssertEqualOperation(
        "5.response.body.data.partner",
        """{
            "name": "{{3.request.body.partner.name}}",
            "address": "{{3.request.body.partner.address}}",
            "phone": "", "folder": "",
            "id": {{5.response.body.data.partner.id}}
        }""",
    )
)
get_order.add_post_operation(AssertEqualOperation("5.response.body.data.order", None))
get_order.add_post_operation(
    AssertEqualOperation(
        "5.response.body.data.number",
        "{{2.request.body.date.substr(0,4)}}{{2.request.body.date.substr(5,7)}}{{2.request.body.date.substr(8,10)}}0001",
    )
)
get_order.add_post_operation(
    AssertEqualOperation("5.response.body.data.amount", "{{3.request.body.amount}}")
)
get_order.add_post_operation(
    AssertEqualOperation(
        "5.response.body.data.prepayment", "{{3.request.body.prepayment}}"
    )
)
get_order.add_post_operation(
    AssertEqualOperation("5.response.body.data.payment", "{{3.request.body.payment}}")
)
get_order.add_post_operation(
    AssertEqualOperation(
        "5.response.body.data.delivered", "{{3.request.body.delivered}}"
    )
)
get_order.add_post_operation(
    AssertEqualOperation(
        "5.response.body.data.invoiceItems.0",
        """{
            "id": {{2.response.body.data.invoiceItems.1.id}},
            "orderItem": null,
            "product": {
                "id": {{2.response.body.data.invoiceItems.1.product.id}},
                "material": "{{2.request.body.invoiceItems.1.product.material}}",
                "name": "{{2.request.body.invoiceItems.1.product.name}}",
                "spec": "{{2.request.body.invoiceItems.1.product.spec}}",
                "unit": "{{2.request.body.invoiceItems.1.product.unit}}",
                "quantity": 0
            },
            "price": {{3.request.body.invoiceItems.0.price}},
            "quantity": {{3.request.body.invoiceItems.0.quantity}},
            "originalAmount": {{3.request.body.invoiceItems.0.originalAmount}},
            "discount": {{3.request.body.invoiceItems.0.discount}},
            "amount": {{3.request.body.invoiceItems.0.amount}},
            "weight": {{3.request.body.invoiceItems.0.weight}},
            "remark": "{{3.request.body.invoiceItems.0.remark}}",
            "delivered": {{3.request.body.invoiceItems.0.delivered}}
        }""",
    )
)
get_order.add_post_operation(
    AssertEqualOperation(
        "5.response.body.data.invoiceItems.1",
        """{
            "id": {{2.response.body.data.invoiceItems.2.id}},
            "orderItem": null,
            "product": {
                "id": {{5.response.body.data.invoiceItems.1.product.id}},
                "material": "{{3.request.body.invoiceItems.1.product.material}}",
                "name": "{{3.request.body.invoiceItems.1.product.name}}",
                "spec": "{{3.request.body.invoiceItems.1.product.spec}}",
                "unit": "{{3.request.body.invoiceItems.1.product.unit}}",
                "quantity": 0
            },
            "price": {{3.request.body.invoiceItems.1.price}},
            "quantity": {{3.request.body.invoiceItems.1.quantity}},
            "originalAmount": {{3.request.body.invoiceItems.1.originalAmount}},
            "discount": {{3.request.body.invoiceItems.1.discount}},
            "amount": {{3.request.body.invoiceItems.1.amount}},
            "weight": null,
            "remark": "{{3.request.body.invoiceItems.1.remark}}",
            "delivered": {{3.request.body.invoiceItems.1.delivered}}
        }""",
    )
)
get_order.add_post_operation(
    AssertEqualOperation(
        "5.response.body.data.invoiceItems.2",
        """{
            "id": {{5.response.body.data.invoiceItems.2.id}},
            "orderItem": null,
            "product": {
                "id": {{2.response.body.data.invoiceItems.0.product.id}},
                "material": "{{2.request.body.invoiceItems.0.product.material}}",
                "name": "{{2.request.body.invoiceItems.0.product.name}}",
                "spec": "{{2.request.body.invoiceItems.0.product.spec}}",
                "unit": "{{2.request.body.invoiceItems.0.product.unit}}",
                "quantity": 0
            },
            "price": {{3.request.body.invoiceItems.2.price}},
            "quantity": {{3.request.body.invoiceItems.2.quantity}},
            "originalAmount": {{3.request.body.invoiceItems.2.originalAmount}},
            "discount": {{3.request.body.invoiceItems.2.discount}},
            "amount": {{3.request.body.invoiceItems.2.amount}},
            "weight": {{3.request.body.invoiceItems.2.weight}},
            "remark": "{{3.request.body.invoiceItems.2.remark}}",
            "delivered": {{3.request.body.invoiceItems.2.delivered}}
        }""",
    )
)
t.add_step(get_order)  # 5

# 查询所有invoice
get_all_invoice = Step("get", "/invoices", "查询所有invoice")
get_all_invoice.add_post_operation(
    AssertEqualOperation("6.response.body.data.length", 1)
)
t.add_step(get_all_invoice)  # 6

# 查询所有partner
get_all_partner = Step("get", "/partners", "查询所有partner")
get_all_partner.add_post_operation(
    AssertEqualOperation("7.response.body.data.length", 2)
)
t.add_step(get_all_partner)  # 7

# 查询所有product
get_all_product = Step("get", "/products", "查询所有product")
get_all_product.add_post_operation(
    AssertEqualOperation("8.response.body.data.length", 4)
)
t.add_step(get_all_product)  # 8

# 查询所有invoiceItem
get_all_invoice_item = Step("get", "/invoiceItems", "查询所有invoiceItem")
get_all_invoice_item.add_post_operation(
    AssertEqualOperation("9.response.body.data.length", 3)
)
t.add_step(get_all_invoice_item)  # 9

# 删除user
delete_user = Step(
    "delete",
    "/users/{id}",
    "删除user",
    path_params='{"id": {{1.response.body.data.id}}}',
)
t.add_step(delete_user)  # 10

t.run()
