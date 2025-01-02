from lib.api import Api
from lib.utils import set_global_variables, assertion

#
# 创建order，同时创建部分product
#
# - 创建order时，`invoiceItems.product.material`可以不包含，保存到数据库中会自动转为`""`。
# - 创建order时，`invoiceItems.product.quantity`可以不包含，保存到数据库中会自动转为`0`。
# - 创建order时，`invoiceItems.weight`可以不包含，保存到数据库中会自动转为`null`。
# - 创建order时，`order`可以为`{ id: null }`或不包含，保存时只会是`null`。【这里测试的是不包含】
# - 创建order时，已存在的product，不可以更改信息。
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

# 创建partner
partner = {
    "name": "name#1",
    "phone": "phone#1",
    "address": "address#1",
    "folder": "folder#1"
}
create_partner = Api('post', '/partners', body=partner)
create_partner.run()

# 创建order
order = {
    "type": 0,
    "partner": {
        "id": create_partner.get_variable('response.body.data.id')
    },
    "date": "2024-05-20",
    "invoiceItems": [
        {
            "product": {
                "id": create_product.get_variable('response.body.data.id'),
                "name": "shouldn't appear"
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 0,
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
            "price": 104330,
            "quantity": 243,
            "originalAmount": 20320,
            "discount": 80,
            "amount": 3423,
            "weight": None,
            "remark": "remark#2",
            "delivered": True
        },
        {
            "product": {
                "name": "name#3",
                "spec": "spec#3",
                "unit": "unit#3"
            },
            "price": 465,
            "quantity": 532,
            "originalAmount": 205430,
            "discount": 100,
            "amount": 165430,
            "remark": "remark#3",
            "delivered": False
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 2
}
create_order = Api('post', '/invoices', body=order)
create_order.run()
created_order_id = create_order.get_variable('response.body.data.id')

# 查询单个order
get_order = Api('get', '/invoices/{id}', path_params={"id": create_order.get_variable('response.body.data.id')})
get_order.run()

# 查询所有invoice
get_all_invoice = Api('get', '/invoices')
get_all_invoice.run()

# 查询所有product
get_all_product = Api('get', '/products')
get_all_product.run()

# 查询所有partner
get_all_partner = Api('get', '/partners')
get_all_partner.run()

# 查询所有invoiceItem
get_all_invoice_item = Api('get', '/invoiceItems')
get_all_invoice_item.run()

# 删除user
delete_user = Api('delete', '/users/{id}', path_params={"id": login_user_id})
delete_user.run()