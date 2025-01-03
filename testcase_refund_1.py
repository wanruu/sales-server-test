from lib.api import Api
from lib.utils import set_global_variables, assertion

#
# 创建refund
#
# - 创建refund时，不可以新增`product`。
# - 创建refund时，必须指定`invoiceItems.orderItem`，否则报`400`。如果对应`orderItem`不存在，报`404`。
#

# 创建user
user = {"name": "Hermione", "password": "12345678"}
create_user = Api('post', '/users', body=user)
create_user.run()

# 登录
login_user = Api('post', '/users/login', body=user, expected_status_code=200)
login_user.add_operation('post', lambda cur: set_global_variables("access_token", cur.get_variable('response.body.data.accessToken')))
login_user.run()
login_user_id = login_user.get_variable('response.body.data.id')


# 创建order
order = {
    "type": 0,
    "partner": {
        "name": "partner#1"
    },
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
}
create_order = Api('post', '/invoices', body=order)
create_order.run()
order_id = create_order.get_variable('response.body.data.id')

# 创建refund，product id不可以为空
refund = {
    "type": 2,
    "partner": {
        "id": create_order.get_variable('response.body.data.partner.id')
    },
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
            "orderItem":{ "id": create_order.get_variable('response.body.data.invoiceItems[0].id') }
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 0,
    "order": { "id": order_id }
}
create_refund = Api('post', '/invoices', body=refund, expected_status_code=400)
create_refund.run()

# 创建refund，orderItem不可以为空
refund = {
    "type": 2,
    "partner": {
        "id": create_order.get_variable('response.body.data.partner.id')
    },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
              "id": create_order.get_variable('response.body.data.invoiceItems[0].product.id')
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
}
create_refund = Api('post', '/invoices', body=refund, expected_status_code=400)
create_refund.run()

# 创建refund，orderItem id不可以为null
refund = {
    "type": 2,
    "partner": {
        "id": create_order.get_variable('response.body.data.partner.id')
    },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
              "id": create_order.get_variable('response.body.data.invoiceItems[0].product.id')
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
}
create_refund = Api('post', '/invoices', body=refund, expected_status_code=400)
create_refund.run()

# 创建refund，orderItem id不可以为不存在的值
refund = {
    "type": 2,
    "partner": {
        "id": create_order.get_variable('response.body.data.partner.id')
    },
    "date": "2025-09-29",
    "invoiceItems": [
        {
            "product": {
              "id": create_order.get_variable('response.body.data.invoiceItems[0].product.id')
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
}
create_refund = Api('post', '/invoices', body=refund, expected_status_code=404)
create_refund.run()

# 创建refund
refund = {
    "type": 2,
    "partner": {
        "id": create_order.get_variable('response.body.data.partner.id')
    },
    "date": create_order.get_variable('request.body.date'),
    "invoiceItems": [
        {
            "product": {
              "id": create_order.get_variable('response.body.data.invoiceItems[0].product.id')
            },
            "price": 1000,
            "quantity": 20,
            "originalAmount": 2000,
            "discount": 100,
            "amount": 1600,
            "remark": "remark#refund#1",
            "delivered": True,
            "orderItem": {
                "id": create_order.get_variable('response.body.data.invoiceItems[0].id')
            }
        }
    ],
    "amount": 423,
    "prepayment": 432,
    "payment": 34,
    "delivered": 1,
    "order": { "id": order_id }
}
create_refund = Api('post', '/invoices', body=refund)
create_refund.add_operation('post', lambda cur: assertion(
  cur.get_variable("response.body.data.invoiceItems[0].product.id"),
  '==', 
  create_order.get_variable('response.body.data.invoiceItems[0].product.id')
))
create_refund.add_operation('post', lambda cur: assertion(
  cur.get_variable("response.body.data.invoiceItems[0].orderItem.id"),
  '==', 
  create_order.get_variable('response.body.data.invoiceItems[0].id')
))
create_refund.add_operation('post', lambda cur: assertion(
  cur.get_variable("response.body.data.partner.id"),
  '==', 
  create_order.get_variable('response.body.data.partner.id')
))
create_refund.add_operation('post', lambda cur: assertion(cur.get_variable("response.body.data.order.id"),'==', order_id))
create_refund.run()
refund_id = create_refund.get_variable('response.body.data.id')

# 查询单个refund
query_refund = Api('get', '/invoices/{id}', path_params={"id": refund_id})
query_refund.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.number'), '==', create_refund.get_variable('request.body.date').replace('-', '') + '0001'))
query_refund.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.partner.name'), '==', create_order.get_variable('request.body.partner.name')))
query_refund.run()

# 查询单个order
query_order = Api('get', '/invoices/{id}', path_params={"id": order_id})
query_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.number'), '==', create_order.get_variable('request.body.date').replace('-', '') + '0001'))
query_order.run()

# 删除user
delete_user = Api('delete', '/users/{id}', path_params={"id": login_user_id})
delete_user.run()