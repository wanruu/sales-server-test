from lib.api import Api
from lib.utils import set_global_variables, assertion
import pydash

#
# 创建order，同时创建partner和部分product
#
# - 创建order时，`order`可以为`null`或不包含，保存时只会是`null`。【这里测试的是`null`】
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

# 创建product
product = {
    "material": "material#1",
    "name": "name#1",
    "spec": "spec#1",
    "unit": "unit#1",
    "quantity": 10,
}
create_product = Api('post', '/products', body=product)
create_product.run()

# 创建order
order = {
    "type": 0,
    "partner": {
        "name": "name#1",
        "address": "address#1"
    },
    "date": "2024-05-20",
    "invoiceItems": [
        {
            "product": {
                "id": create_product.get_variable('response.body.data.id'),
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
}
create_order = Api('post', '/invoices', body=order)
create_order.run()

# 查询单个partner
get_partner = Api('get', '/partners/{id}', path_params={"id": create_order.get_variable('response.body.data.partner.id')})
get_partner.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.name'), '==', create_order.get_variable('request.body.partner.name')))
get_partner.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.address'), '==', create_order.get_variable('request.body.partner.address')))
get_partner.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.folder'), '==', ''))
get_partner.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.phone'), '==', ''))
get_partner.run()

# 查询单个order
get_order = Api('get', '/invoices/{id}', path_params={"id": create_order.get_variable('response.body.data.id')})
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.partner'), '==', get_partner.get_variable('response.body.data')))
get_order.run()

# 查询所有product
get_all_product = Api('get', '/products')
get_all_product.add_operation('post', lambda cur: assertion(len(cur.get_variable('response.body.data')), '==', 2))
get_all_product.run()

# 查询所有invoice
get_all_invoice = Api('get', '/invoices')
get_all_invoice.add_operation('post', lambda cur: assertion(len(cur.get_variable('response.body.data')), '==', 1))
get_all_invoice.run()

# 删除user
delete_user = Api('delete', '/users/{id}', path_params={"id": login_user_id})
delete_user.run()