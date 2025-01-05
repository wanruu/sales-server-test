from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariableOperation, AssertEqualOperation
import json

#
# 创建order，同时创建部分product
#
# - 创建order时，`invoiceItems.product.material`可以不包含，保存到数据库中会自动转为`""`。
# - 创建order时，`invoiceItems.product.quantity`可以不包含，保存到数据库中会自动转为`0`。
# - 创建order时，`invoiceItems.weight`可以不包含，保存到数据库中会自动转为`null`。
# - 创建order时，`order`可以为`null`或不包含，保存时只会是`null`。【这里测试的是不包含】
# - 创建order时，已存在的product，不可以更改信息。
#

t = Testcase('创建order，同时创建部分product', '''
- 创建order时，`invoiceItems.product.material`可以不包含，保存到数据库中会自动转为`""`。
- 创建order时，`invoiceItems.product.quantity`可以不包含，保存到数据库中会自动转为`0`。
- 创建order时，`invoiceItems.weight`可以不包含，保存到数据库中会自动转为`null`。
- 创建order时，`order`可以为`null`或不包含，保存时只会是`null`。【这里测试的是不包含】
- 创建order时，已存在的product，不可以更改信息。''')

# 创建user
user = json.dumps({"name": "Hermione", "password": "12345678"})
create_user = Step('post', '/users', '创建user', body=user)
t.add_step(create_user) #0

# 登录
login_user = Step('post', '/users/login', '登录', body=user, expected_status_code=200)
login_user.add_post_operation(SetGlobalVariableOperation('access_token', '{{1.response.body.data.accessToken}}'))
t.add_step(login_user) #1

# 创建product
product = json.dumps({
    "material": "material#1",
    "name": "name#1",
    "spec": "spec#1",
    "unit": "unit#1",
    "quantity": 10,
})
create_product = Step('post', '/products', '创建product', body=product)
t.add_step(create_product) #2

# 创建partner
partner = json.dumps({
    "name": "name#1",
    "phone": "phone#1",
    "address": "address#1",
    "folder": "folder#1"
})
create_partner = Step('post', '/partners', '创建partner', body=partner)
t.add_step(create_partner) #3

# 创建order
order = '''{
    "type": 0,
    "partner": {
        "id": {{3.response.body.data.id}}
    },
    "date": "2024-05-20",
    "invoiceItems": [
        {
            "product": {
                "id": {{2.response.body.data.id}},
                "name": "shouldn't appear"
            },
            "price": 100,
            "quantity": 2,
            "originalAmount": 200,
            "discount": 0,
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
            "price": 104330,
            "quantity": 243,
            "originalAmount": 20320,
            "discount": 80,
            "amount": 3423,
            "weight": null,
            "remark": "remark#2",
            "delivered": true
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
            "delivered": false
        }
    ],
    "amount": 1000,
    "prepayment": 50,
    "payment": 200,
    "delivered": 2
}'''
create_order = Step('post', '/invoices', '创建order', body=order)
t.add_step(create_order) #4

# 查询单个order
get_order = Step('get', '/invoices/{id}', '查询单个order', path_params='{"id": {{4.response.body.data.id}}}')
get_order.add_post_operation(AssertEqualOperation('5.response.body.data.partner', '{{3.response.body.data}}'))
get_order.add_post_operation(AssertEqualOperation('5.response.body.data.order', None))
# get_order.assert_equal('response.body.data.number', create_order.get_variable('request.body.date').replace('-', '') + '0001')
get_order.add_post_operation(AssertEqualOperation('5.response.body.data.type', '{{4.request.body.type}}'))
get_order.add_post_operation(AssertEqualOperation('5.response.body.data.amount', '{{4.request.body.amount}}'))
get_order.add_post_operation(AssertEqualOperation('5.response.body.data.prepayment', '{{4.request.body.prepayment}}'))
get_order.add_post_operation(AssertEqualOperation('5.response.body.data.payment', '{{4.request.body.payment}}'))
get_order.add_post_operation(AssertEqualOperation('5.response.body.data.delivered', '{{4.request.body.delivered}}'))
# get_order.assert_equal('response.body.data.invoiceItems[0]', 
#     lambda cur: pydash.merge(
#         create_order.get_variable('request.body.invoiceItems.[0]'),
#         {
#             "id": cur.get_variable('response.body.data.invoiceItems.[0].id'), # not check
#             "product": create_product.get_variable('response.body.data'),
#             "orderItem": None,
#         },
#     )
# )
# get_order.assert_equal('response.body.data.invoiceItems[1]', 
#     lambda cur: pydash.merge(
#         create_order.get_variable('request.body.invoiceItems.[1]'),
#         {
#             "id": cur.get_variable('response.body.data.invoiceItems.[1].id'), # not check
#             "product": pydash.merge(
#                 {"id": cur.get_variable('response.body.data.invoiceItems.[1].product.id')},
#                 cur.get_variable('request.body.invoiceItems.[1].product'),
#             ),
#             "orderItem": None,
#         },
#     )
# )
# get_order.assert_equal('response.body.data.invoiceItems[2]', 
#     lambda cur: pydash.merge(
#         create_order.get_variable('request.body.invoiceItems.[2]'),
#         {
#             "id": cur.get_variable('response.body.data.invoiceItems.[2].id'), # not check
#             "product": pydash.merge(
#                 create_order.get_variable('request.body.invoiceItems.[2].product'),
#                 {
#                     "id": cur.get_variable('response.body.data.invoiceItems.[2].product.id'),
#                     "material": "",
#                     "quantity": 0,
#                 },
#             ),
#             "weight": None,
#             "orderItem": None,
#         },
#     )
# )
t.add_step(get_order) #5

# 查询所有invoice
get_all_invoice = Step('get', '/invoices', '查询所有invoice')
get_all_invoice.add_post_operation(AssertEqualOperation('6.response.body.data.length', 1))
t.add_step(get_all_invoice) #6

# 查询所有product
get_all_product = Step('get', '/products', '查询所有product')
get_all_product.add_post_operation(AssertEqualOperation('7.response.body.data.length', 3))
t.add_step(get_all_product) #7

# 查询所有partner
get_all_partner = Step('get', '/partners', '查询所有partner')
get_all_partner.add_post_operation(AssertEqualOperation('8.response.body.data.length', 1))
t.add_step(get_all_partner) #8

# 查询所有invoiceItem
get_all_invoice_item = Step('get', '/invoiceItems', '查询所有invoiceItem')
get_all_invoice_item.add_post_operation(AssertEqualOperation('9.response.body.data.length', 3))
t.add_step(get_all_invoice_item) #9

# 删除user
delete_user = Step('delete', '/users/{id}', '删除user', path_params='{"id": {{1.response.body.data.id}}}')
t.add_step(delete_user) #10

t.run()