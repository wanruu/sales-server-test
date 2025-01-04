from lib.step import Step
from lib.utils import custom_get
from lib.operation import SetGlobalVariableOperation, AssertEqualOperation
import json

#
# 创建refund
#
# - 创建refund时，不可以新增`product`。
# - 创建refund时，必须指定`invoiceItems.orderItem`，否则报`400`。如果对应`orderItem`不存在，报`404`。
#

# 创建user
user = '{"name": "Hermione", "password": "12345678"}'
create_user = Step('post', '/users', '创建user', body=user)
create_user.run()

# 登录
login_user = Step('post', '/users/login', '登录', body=user, expected_status_code=200)
login_user.add_post_operation(SetGlobalVariableOperation('access_token', '{{response.body.data.accessToken}}'))
login_user.run()
login_user_id = custom_get(login_user, 'response.body.data.id')

# 创建order
order = json.dumps({
    "type": 0,
    "partner": { "name": "partner#1" },
    "date": "2025-10-12",
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
            "delivered": False,
            "orderItem":{ "id": 1 }
        },
        {
            "product": {
                "material": "material#2",
                "name": "name#2",
                "spec": "spec#2",
                "unit": "unit#2"
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "weight": 50,
            "remark": "remark#2",
            "delivered": False,
            "orderItem": None
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": None
})
create_order = Step('post', '/invoices', '创建order', body=order)
create_order.run()
order_id = custom_get(create_order, 'response.body.data.id')

# 创建refund，product id不可以为空
refund = json.dumps({
    "type": 2,
    "partner": { "id": custom_get(create_order, 'response.body.data.partner.id') },
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
            "delivered": False,
            "orderItem":{ "id": custom_get(create_order, 'response.body.data.invoiceItems.0.id') }
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": order_id }
})
create_refund = Step('post', '/invoices', '创建refund，product id不可以为空', body=refund, expected_status_code=400)
create_refund.run()

# 创建refund，orderItem不可以为空
refund = json.dumps({
    "type": 2,
    "partner": {
        "id": custom_get(create_order, 'response.body.data.partner.id')
    },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
              "id": custom_get(create_order, 'response.body.data.invoiceItems.0.product.id')
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "remark": "remark#1",
            "delivered": False,
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": order_id }
})
create_refund = Step('post', '/invoices', '创建refund，orderItem不可以为空', body=refund, expected_status_code=400)
create_refund.run()

# 创建refund，orderItem id不可以为null
refund = json.dumps({
    "type": 2,
    "partner": {
        "id": custom_get(create_order, 'response.body.data.partner.id')
    },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
              "id": custom_get(create_order, 'response.body.data.invoiceItems.0.product.id')
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "remark": "remark#1",
            "delivered": False,
            "orderItem": {
                "id": None
            }
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": order_id }
})
create_refund = Step('post', '/invoices', '创建refund，orderItem id不可以为null', body=refund, expected_status_code=400)
create_refund.run()

# 创建refund，orderItem id不可以为不存在的值
refund = json.dumps({
    "type": 2,
    "partner": {
        "id": custom_get(create_order, 'response.body.data.partner.id')
    },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
              "id": custom_get(create_order, 'response.body.data.invoiceItems.0.product.id')
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "remark": "remark#1",
            "delivered": False,
            "orderItem": {
                "id": 1
            }
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": order_id }
})
create_refund = Step('post', '/invoices', '创建refund，orderItem id不可以为不存在的值', body=refund, expected_status_code=404)
create_refund.run()

# 创建refund
refund = json.dumps({
    "type": 2,
    "partner": {
        "id": custom_get(create_order, 'response.body.data.partner.id')
    },
    "date": custom_get(create_order, 'request.body.date'),
    "invoiceItems": [
        {
            "product": {
              "id": custom_get(create_order, 'response.body.data.invoiceItems.0.product.id')
            },
            "price": 1000,
            "quantity": 20,
            "originalAmount": 2000,
            "discount": 100,
            "amount": 1600,
            "remark": "remark#refund#1",
            "delivered": True,
            "orderItem": {
                "id": custom_get(create_order, 'response.body.data.invoiceItems.0.id')
            }
        }
    ],
    "amount": 423,
    "prepayment": 432,
    "payment": 34,
    "delivered": 1,
    "order": { "id": order_id }
})
create_refund = Step('post', '/invoices', '创建refund', body=refund)
create_refund.add_post_operation(AssertEqualOperation("response.body.data.invoiceItems.0.product.id", custom_get(create_order, 'response.body.data.invoiceItems.0.product.id')))
create_refund.add_post_operation(AssertEqualOperation("response.body.data.invoiceItems.0.orderItem.id", custom_get(create_order, 'response.body.data.invoiceItems.0.id')))
create_refund.add_post_operation(AssertEqualOperation("response.body.data.partner.id", custom_get(create_order, 'response.body.data.partner.id')))
create_refund.add_post_operation(AssertEqualOperation("response.body.data.order.id", order_id))
create_refund.run()
refund_id = custom_get(create_refund, 'response.body.data.id')

# 查询单个refund
query_refund = Step('get', '/invoices/{id}', '查询单个refund', path_params=json.dumps({"id": refund_id}))
query_refund.add_post_operation(AssertEqualOperation("response.body.data.number", custom_get(create_refund, 'request.body.date').replace('-', '') + '0001'))
query_refund.add_post_operation(AssertEqualOperation("response.body.data.partner.name", custom_get(create_order, 'request.body.partner.name')))
query_refund.run()

# 查询单个order
query_order = Step('get', '/invoices/{id}', '查询单个order', path_params=json.dumps({"id": order_id}))
query_order.add_post_operation(AssertEqualOperation("response.body.data.number", custom_get(create_order, 'request.body.date').replace('-', '') + '0001'))
query_order.run()

# 删除user
delete_user = Step('delete', '/users/{id}', '删除user', path_params=json.dumps({"id": login_user_id}))
delete_user.run()