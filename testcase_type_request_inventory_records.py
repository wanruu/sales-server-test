from lib.step import Step
from lib.testcase import Testcase
from lib.operation import SetGlobalVariable
import json
import data

#
# 类型测试 - request - inventory records
#

t = Testcase("类型测试 - request - inventory records")
t.description = ""


# 创建user
user_str = json.dumps(data.accepted_user)
step__create_user = Step("post", "/users", "创建user", body=user_str)
t.add_step(step__create_user)  # 0

# 登录
step__login = Step(
    "post", "/users/login", "登录", body=user_str, expected_status_code=200
)
step__login.add_post_operation(
    SetGlobalVariable("access_token", "{{1.response.body.accessToken}}")
)
t.add_step(step__login)  # 1

# 创建inventory record
for inventory_record in data.accepted_inventory_records:
    inventory_record_str = json.dumps(inventory_record)
    step__create_inventory_record = Step(
        "post", "/inventoryRecords", "创建inventory record", body=inventory_record_str
    )
    t.add_step(step__create_inventory_record)

# # 创建invoice
# for invoice in data.unaccepted_invoices:
#     invoice_str = json.dumps(invoice)
#     step__create_invoice = Step(
#         "post", "/invoices", "创建invoice", body=invoice_str, expected_status_code=400
#     )
#     t.add_step(step__create_invoice)

# 删除user
step__delete_user = Step(
    "delete", "/users/{id}", "删除user", path_params='{ "id": {{1.response.body.id}} }'
)
t.add_step(step__delete_user)


t.run()
