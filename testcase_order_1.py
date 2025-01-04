from lib.step import Step
from lib.testcase import Testcase
from lib.utils import set_global_variables
import pydash

#
# 创建order，同时创建部分product
#
# - 创建order时，`invoiceItems.product.material`可以不包含，保存到数据库中会自动转为`""`。
# - 创建order时，`invoiceItems.product.quantity`可以不包含，保存到数据库中会自动转为`0`。
# - 创建order时，`invoiceItems.weight`可以不包含，保存到数据库中会自动转为`null`。
# - 创建order时，`order`可以为`null`或不包含，保存时只会是`null`。【这里测试的是不包含】
# - 创建order时，已存在的product，不可以更改信息。
#

testcase = Testcase('创建order，同时创建部分product')

# 创建user
user = {"name": "Hermione", "password": "12345678"}
create_user = Step('post', '/users', body=user)
testcase.add_step(create_user) #0

# 登录
login_user = Step('post', '/users/login', body=user, expected_status_code=200)
login_user.add_operation('post', lambda cur: set_global_variables("access_token", cur.get_variable('response.body.data.accessToken')))
testcase.add_step(login_user) #1
# login_user_id = login_user.get_variable('response.body.data.id') TODO

# 创建product
product = {
    "material": "material#1",
    "name": "name#1",
    "spec": "spec#1",
    "unit": "unit#1",
    "quantity": 10,
}
create_product = Step('post', '/products', body=product)
testcase.add_step(create_product) #2

# 创建partner
partner = {
    "name": "name#1",
    "phone": "phone#1",
    "address": "address#1",
    "folder": "folder#1"
}
create_partner = Step('post', '/partners', body=partner)
testcase.add_step(create_partner) #3

# 创建order
order = {
    "type": 0,
    "partner": {
        "id": testcase.get_variable('response.body.data.id')
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
create_order = Step('post', '/invoices', body=order)
create_order.run()

# 查询单个order
get_order = Step('get', '/invoices/{id}', path_params={"id": create_order.get_variable('response.body.data.id')})
get_order.assert_equal('response.body.data.partner', create_partner.get_variable('response.body.data'))
get_order.assert_equal('response.body.data.order', None)
get_order.assert_equal('response.body.data.number', create_order.get_variable('request.body.date').replace('-', '') + '0001')
get_order.assert_equal('response.body.data.type', create_order.get_variable('request.body.type'))
get_order.assert_equal('response.body.data.amount', create_order.get_variable('request.body.amount'))
get_order.assert_equal('response.body.data.prepayment', create_order.get_variable('request.body.prepayment'))
get_order.assert_equal('response.body.data.payment', create_order.get_variable('request.body.payment'))
get_order.assert_equal('response.body.data.delivered', create_order.get_variable('request.body.delivered'))
get_order.assert_equal('response.body.data.invoiceItems[0]', 
    lambda cur: pydash.merge(
        create_order.get_variable('request.body.invoiceItems.[0]'),
        {
            "id": cur.get_variable('response.body.data.invoiceItems.[0].id'), # not check
            "product": create_product.get_variable('response.body.data'),
            "orderItem": None,
        },
    )
)
get_order.assert_equal('response.body.data.invoiceItems[1]', 
    lambda cur: pydash.merge(
        create_order.get_variable('request.body.invoiceItems.[1]'),
        {
            "id": cur.get_variable('response.body.data.invoiceItems.[1].id'), # not check
            "product": pydash.merge(
                {"id": cur.get_variable('response.body.data.invoiceItems.[1].product.id')},
                cur.get_variable('request.body.invoiceItems.[1].product'),
            ),
            "orderItem": None,
        },
    )
)
get_order.assert_equal('response.body.data.invoiceItems[2]', 
    lambda cur: pydash.merge(
        create_order.get_variable('request.body.invoiceItems.[2]'),
        {
            "id": cur.get_variable('response.body.data.invoiceItems.[2].id'), # not check
            "product": pydash.merge(
                create_order.get_variable('request.body.invoiceItems.[2].product'),
                {
                    "id": cur.get_variable('response.body.data.invoiceItems.[2].product.id'),
                    "material": "",
                    "quantity": 0,
                },
            ),
            "weight": None,
            "orderItem": None,
        },
    )
)
get_order.run()


# 查询所有invoice
get_all_invoice = Step('get', '/invoices')
get_all_invoice.assert_equal('response.body.data.length', 1)
get_all_invoice.run()

# 查询所有product
get_all_product = Step('get', '/products')
get_all_product.assert_equal('response.body.data.length', 3)
get_all_product.run()

# 查询所有partner
get_all_partner = Step('get', '/partners')
get_all_partner.assert_equal('response.body.data.length', 1)
get_all_partner.run()

# 查询所有invoiceItem
get_all_invoice_item = Step('get', '/invoiceItems')
get_all_invoice_item.assert_equal('response.body.data.length', 3)
get_all_invoice_item.run()

# 删除user
delete_user = Step('delete', '/users/{id}', path_params={"id": login_user_id})
delete_user.run()