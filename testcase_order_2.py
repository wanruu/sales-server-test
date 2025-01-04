from lib.step import Step
from lib.utils import custom_get
from lib.operation import SetGlobalVariableOperation, AssertEqualOperation
import json


#
# 创建order，同时创建partner和部分product
#
# - 创建order时，`order`可以为`null`或不包含，保存时只会是`null`。【这里测试的是`null`】
#

# 创建user
user = json.dumps({"name": "Hermione", "password": "12345678"})
create_user = Step('post', '/users', '创建user', body=user)
create_user.run()

# 登录
login_user = Step('post', '/users/login', '登录', body=user, expected_status_code=200)
login_user.add_post_operation(SetGlobalVariableOperation('access_token', '{{response.body.data.accessToken}}'))
login_user.run()
login_user_id = custom_get(login_user, 'response.body.data.id')

# 创建product
product = json.dumps({
    "material": "material#1",
    "name": "name#1",
    "spec": "spec#1",
    "unit": "unit#1",
    "quantity": 10,
})
create_product = Step('post', '/products', '创建product', body=product)
create_product.run()

# 创建order
order = json.dumps({
    "type": 0,
    "partner": {
        "name": "name#1",
        "address": "address#1"
    },
    "date": "2024-05-20",
    "invoiceItems": [
        {
            "product": {
                "id": custom_get(create_product, 'response.body.data.id')
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 80,
            "amount": 160,
            "weight": 50,
            "remark": "remark#1",
            "delivered": True
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
            "weight": None,
            "remark": "remark#2",
            "delivered": True
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 2,
    "order": None
})
create_order = Step('post', '/invoices', '创建order', body=order)
create_order.run()

# 查询单个partner
get_partner = Step('get', '/partners/{id}', '查询单个partner', path_params=json.dumps({"id": custom_get(create_order, 'response.body.data.partner.id')}))
get_partner.add_post_operation(AssertEqualOperation('response.body.data.name', custom_get(create_order, 'request.body.partner.name')))
get_partner.add_post_operation(AssertEqualOperation('response.body.data.address', custom_get(create_order, 'request.body.partner.address')))
get_partner.add_post_operation(AssertEqualOperation('response.body.data.folder', ''))
get_partner.add_post_operation(AssertEqualOperation('response.body.data.phone', ''))
get_partner.run()

# 查询单个order
get_order = Step('get', '/invoices/{id}', '查询单个order', path_params=json.dumps({"id": custom_get(create_order, 'response.body.data.id')}))
get_order.add_post_operation(AssertEqualOperation('response.body.data.partner', json.dumps(custom_get(get_partner, 'response.body.data'))))
get_order.run()

# 查询所有product
get_all_product = Step('get', '/products', '查询所有product')
get_all_product.add_post_operation(AssertEqualOperation('response.body.data.length', 2))
get_all_product.run()

# 查询所有invoice
get_all_invoice = Step('get', '/invoices', '查询所有invoice')
get_all_invoice.add_post_operation(AssertEqualOperation('response.body.data.length', 1))
get_all_invoice.run()

# 删除user
delete_user = Step('delete', '/users/{id}', '删除user', path_params=json.dumps({ "id": login_user_id }))
delete_user.run()