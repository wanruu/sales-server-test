from lib.api import Api
from lib.utils import set_global_variables, assertion
import pydash

#
# 修改order
#
# - 更新order时，`type`和`number`不可以更改。
# - 更新order时，可以新增`partner`，但不可以修改原有的`partner`。【这里测试的是新增】
# - 更新order时，不在列表里的`invoiceItem`应该被删除。
# - 更新order时，在列表里的`invoiceItem`如果带`id`，其数据应该更新，`id`不改变，可以新增`product`，但不可以更改原有的`product`。
# - 更新order时，在列表里的`invoiceItem`如果不带`id`，则应该新建。可以新增`product`，但不可以更改原有的`product`。
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
        "name": "partner#1",
        "folder": "folder#1"
    },
    "date": "2024-05-20",
    "invoiceItems": [
        {
            "product": {
                "material": "material#1",
                "name": "name#1",
                "spec": "spec#1",
                "unit": "unit#1"
            },
            "price": 432,
            "quantity": 432,
            "originalAmount": 567,
            "discount": 80,
            "amount": 25,
            "weight": 643,
            "remark": "remark#1",
            "delivered": True
        },
        {
            "product": {
                "material": "material#2",
                "name": "name#2",
                "spec": "spec#2",
                "unit": "unit#2"
            },
            "price": 643,
            "quantity": 24,
            "originalAmount": 654,
            "discount": 100,
            "amount": 52,
            "weight": 525,
            "remark": "remark#2",
            "delivered": True
        },
        {
            "product": {
                "material": "material#3",
                "name": "name#3",
                "spec": "spec#3",
                "unit": "unit#3"
            },
            "price": 42,
            "quantity": 425,
            "originalAmount": 12423,
            "discount": 80,
            "amount": 8645,
            "weight": 345,
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

# 更新order
order_update = {
    "type": 0,
    "partner": {
        "name": "partner#2",
        "address": "address#2"
    },
    "date": "2000-05-20",
    "invoiceItems": [
        {
            "id": create_order.get_variable('response.body.data.invoiceItems.[1].id'),
            "product": {
                "id": create_order.get_variable('response.body.data.invoiceItems.[1].product.id'),
                "name": "shouldn't appear"
            },
            "price": 1,
            "quantity": 1,
            "originalAmount": 1,
            "discount": 1,
            "amount": 1,
            "weight": 1,
            "remark": "1",
            "delivered": False
        },
        {
            "id": create_order.get_variable('response.body.data.invoiceItems.[2].id'),
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
            "delivered": True
        },
        {
            "product": {
                "id": create_order.get_variable('response.body.data.invoiceItems.[0].product.id')
            },
            "price": 3,
            "quantity": 3,
            "originalAmount": 3,
            "discount": 3,
            "amount": 3,
            "weight": None,
            "remark": "3",
            "delivered": True
        }
    ],
    "amount": 1,
    "prepayment": 1,
    "payment": 1,
    "delivered": 1
}
update_order = Api('put', '/invoices/{id}', path_params={"id": create_order.get_variable('response.body.data.id')}, body=order_update)
update_order.run()

# 查询单个partner
get_partner = Api('get', '/partners/{id}', path_params={"id": create_order.get_variable('response.body.data.partner.id')})
get_partner.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.name'), '==', create_order.get_variable('request.body.partner.name')))
get_partner.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.folder'), '==', create_order.get_variable('request.body.partner.folder')))
get_partner.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.address'), '==', ''))
get_partner.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.phone'), '==', ''))
get_partner.run()

# 查询单个order
get_order = Api('get', '/invoices/{id}', path_params={"id": create_order.get_variable('response.body.data.id')})
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.partner'), '==', 
    pydash.merge(
        update_order.get_variable('request.body.partner'),
        {"phone": "", "folder": "", "id": cur.get_variable('response.body.data.partner.id')}
    )
))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.order'), '==', None))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.number'), '==', create_order.get_variable('request.body.date').replace('-', '') + '0001'))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.type'), '==', create_order.get_variable('request.body.type')))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.amount'), '==', update_order.get_variable('request.body.amount')))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.prepayment'), '==', update_order.get_variable('request.body.prepayment')))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.payment'), '==', update_order.get_variable('request.body.payment')))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.delivered'), '==', update_order.get_variable('request.body.delivered')))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.invoiceItems[0]'), '==', 
    pydash.merge(
        update_order.get_variable('request.body.invoiceItems.[0]'),
        {
            "id": create_order.get_variable('response.body.data.invoiceItems[1].id'),
            "product": pydash.merge(
                create_order.get_variable('request.body.invoiceItems[1].product'),
                {"quantity": 0, "id": create_order.get_variable('response.body.data.invoiceItems[1].product.id')},
            ),
            "orderItem": None,
        },
    )
))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.invoiceItems[1]'), '==', 
    pydash.merge(
        update_order.get_variable('request.body.invoiceItems.[1]'),
        {
            "id": create_order.get_variable('response.body.data.invoiceItems[2].id'),
            "product": pydash.merge(
                update_order.get_variable('request.body.invoiceItems[1].product'),
                {"quantity": 0, "id": cur.get_variable('response.body.data.invoiceItems[1].product.id')},
            ),
            "weight": None,
            "orderItem": None,
        },
    )
))
get_order.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.invoiceItems[2]'), '==', 
    pydash.merge(
        update_order.get_variable('request.body.invoiceItems.[2]'),
        {
            "id": cur.get_variable('response.body.data.invoiceItems.[2].id'), # not check
            "product": pydash.merge(
                create_order.get_variable('request.body.invoiceItems.[0].product'),
                {"quantity": 0, "id": create_order.get_variable('response.body.data.invoiceItems.[0].product.id')},
            ),
            "orderItem": None,
        },
    )
))
get_order.run()

# 查询所有invoice
get_all_invoice = Api('get', '/invoices')
get_all_invoice.add_operation('post', lambda cur: assertion(len(cur.get_variable('response.body.data')), '==', 1))
get_all_invoice.run()

# 查询所有partner
get_all_partner = Api('get', '/partners')
get_all_partner.add_operation('post', lambda cur: assertion(len(cur.get_variable('response.body.data')), '==', 2))
get_all_partner.run()

# 查询所有product
get_all_product = Api('get', '/products')
get_all_product.add_operation('post', lambda cur: assertion(len(cur.get_variable('response.body.data')), '==', 4))
get_all_product.run()

# 查询所有invoiceItem
get_all_invoice_item = Api('get', '/invoiceItems')
get_all_invoice_item.add_operation('post', lambda cur: assertion(len(cur.get_variable('response.body.data')), '==', 3))
get_all_invoice_item.run()

# 删除user
delete_user = Api('delete', '/users/{id}', path_params={"id": login_user_id})
delete_user.run()