from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable
import json

#
# 类型测试 - response
#

t = Testcase("类型测试 - response")
t.description = "检查每个API返回的response body类型是否正确"


# --------------------- create ---------------------
desc = "创建user"
user = json.dumps({"name": "Hermione", "password": "Ss123456"})
step__create_user = Step("post", "/users", desc, body=user)
t.add_step(step__create_user)  # 0

desc = "登录"
step__login = Step("post", "/users/login", desc, body=user, expected_status_code=200)
step__login.add_post_operation(
    SetGlobalVariable("access_token", "{{1.response.body.accessToken}}")
)
t.add_step(step__login)  # 1

desc = "创建partner"
partner = json.dumps({"name": "Partner name", "address": "Partner address"})
step__create_partner = Step("post", "/partners", desc, body=partner)
t.add_step(step__create_partner)  # 2

desc = "创建product"
product = json.dumps(
    {
        "material": "Product material",
        "name": "Product name",
        "spec": "Product spec",
        "unit": "K",
    }
)
step__create_product = Step("post", "/products", desc, body=product)
t.add_step(step__create_product)  # 3

desc = "创建sales order"
sales_order = """{
    "type": 0,
    "date": "2020-10-10",
    "partner": {"id": {{2.response.body.id}}},
    "invoiceItems": [
        {
            "product": {"id": {{3.response.body.id}}},
            "quantity": "5",
            "price": "100",
            "originalAmount": "500",
            "discount": 80,
            "amount": "400",
            "remark": "hello world",
            "deliveryStatus": 0
        }
    ],
    "amount": "400",
    "prepayment": "0",
    "payment": "200",
    "deliveryStatus": 0
}"""
step__create_invoice = Step("post", "/invoices", desc, body=sales_order)
t.add_step(step__create_invoice)  # 4

desc = "查询单个sales order，以获取创建sales return需要的数据"
step__get_sales_order = Step(
    "get",
    "/invoices/{id}",
    desc,
    path_params='{ "id": {{4.response.body.id}} }',
)
t.add_step(step__get_sales_order)  # 5

desc = "创建sales return"
sales_return = """{
    "type": 2,
    "date": "2020-10-10",
    "partner": {"id": {{2.response.body.id}}},
    "invoiceItems": [
        {
            "product": {"id": {{3.response.body.id}}},
            "quantity": "5",
            "price": "100",
            "originalAmount": "500",
            "discount": 80,
            "amount": "400",
            "remark": "hello world",
            "deliveryStatus": 1,
            "orderItem": {"id": {{5.response.body.invoiceItems.0.id}}}
        }
    ],
    "order": {"id": {{5.response.body.id}}},
    "amount": "100",
    "prepayment": "0",
    "payment": "100",
    "deliveryStatus": 1
}"""
step__create_sales_return = Step("post", "/invoices", desc, body=sales_return)
t.add_step(step__create_sales_return)  # 6

desc = "创建inventory record"
inventory_record = """{
    "type": 0,
    "quantity": "100",
    "weight": null,
    "remark": "hello world",
    "status": 0,
    "completedAt": "2025-01-23T13:50:59Z",
    "operator": "wendy",
    "product": {"id": {{3.response.body.id}}}
}"""
step__create_inventory_record = Step(
    "post", "/inventoryRecords", desc, body=inventory_record
)
t.add_step(step__create_inventory_record)  # 7

# --------------------- update ---------------------
desc = "更新单个user"
step__update_user = Step(
    "patch",
    "/users/{id}",
    desc,
    path_params='{ "id": {{1.response.body.id}} }',
    body=json.dumps({"name": "Hermione-updated"}),
)
t.add_step(step__update_user)

desc = "更新单个partner"
step__update_partner = Step(
    "patch",
    "/partners/{id}",
    desc,
    path_params='{ "id": {{2.response.body.id}} }',
    body='{ "name": "Hogwarts-updated" }',
)
t.add_step(step__update_partner)

desc = "更新单个product"
step__update_product = Step(
    "patch",
    "/products/{id}",
    desc,
    path_params='{ "id": {{3.response.body.id}} }',
    body='{ "name": "Ravenclaw-updated" }',
)
t.add_step(step__update_product)

desc = "更新sales order"
step__update_sales_order = Step(
    "put",
    "/invoices/{id}",
    desc,
    body=sales_order,
    path_params='{ "id": {{4.response.body.id}} }',
)
t.add_step(step__update_sales_order)

desc = "更新inventory record"
step__update_inventory_record = Step(
    "patch",
    "/inventoryRecords/{id}",
    desc,
    body=inventory_record,
    path_params='{ "id": {{7.response.body.id}} }',
)
t.add_step(step__update_inventory_record)

# --------------------- find ---------------------
desc = "查询单个user"
get_user = Step(
    "get", "/users/{id}", desc, path_params='{ "id": {{1.response.body.id}} }'
)
t.add_step(get_user)

desc = "查询单个partner"
get_partner = Step(
    "get",
    "/partners/{id}",
    desc,
    path_params='{ "id": {{2.response.body.id}} }',
)
t.add_step(get_partner)

desc = "查询全部partner"
get_partners = Step("get", "/partners", desc)
t.add_step(get_partners)

desc = "查询单个product"
get_product = Step(
    "get",
    "/products/{id}",
    desc,
    path_params='{ "id": {{3.response.body.id}} }',
)
t.add_step(get_product)

desc = "查询全部product"
get_products = Step("get", "/products", desc)
t.add_step(get_products)

desc = "查询单个sales order"
get_invoice = Step(
    "get",
    "/invoices/{id}",
    desc,
    path_params='{ "id": {{4.response.body.id}} }',
)
t.add_step(get_invoice)

desc = "查询单个sales return"
get_invoice = Step(
    "get",
    "/invoices/{id}",
    desc,
    path_params='{ "id": {{6.response.body.id}} }',
)
t.add_step(get_invoice)

desc = "查询全部invoice"
get_invoices = Step("get", "/invoices", desc)
t.add_step(get_invoices)

desc = "查询全部sales order"
get_sales_orders = Step("get", "/invoices", desc, query_params='{ "type": 0 }')
t.add_step(get_sales_orders)

desc = "查询partner的invoice"
get_invoices = Step(
    "get",
    "/invoices",
    desc,
    query_params='{ "partnerId": {{2.response.body.id}} }',
)
t.add_step(get_invoices)

desc = "查询product的invoice item"
get_invoice_items = Step(
    "get",
    "/invoiceItems",
    desc,
    query_params='{ "productId": {{3.response.body.id}} }',
)
t.add_step(get_invoice_items)

desc = "查询全部inventory records"
get_inventory_records = Step(
    "get",
    "/inventoryRecords",
    desc,
    path_params='{ "status": [0] }',
)
t.add_step(get_inventory_records)

# --------------------- delete ---------------------
desc = "删除sales order"
delete_invoice = Step(
    "delete",
    "/invoices/{id}",
    desc,
    path_params='{ "id": {{4.response.body.id}} }',
)
t.add_step(delete_invoice)

desc = "删除partner"
delete_partner = Step(
    "delete",
    "/partners/{id}",
    desc,
    path_params='{ "id": {{2.response.body.id}} }',
)
t.add_step(delete_partner)

desc = "删除product"
delete_product = Step(
    "delete",
    "/products/{id}",
    desc,
    path_params='{ "id": {{3.response.body.id}} }',
)
t.add_step(delete_product)

desc = "删除user"
delete_user = Step(
    "delete", "/users/{id}", desc, path_params='{ "id": {{1.response.body.id}} }'
)
t.add_step(delete_user)

t.run()
