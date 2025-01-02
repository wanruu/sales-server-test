from lib.api import Api
from lib.utils import set_global_variables, assertion

#
# 成功创建user并登录修改
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

# 查询user，验证name与创建时一致
find_user = Api('get', '/users/{id}', path_params={"id": login_user_id})
find_user.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.name'), '==', create_user.get_variable('request.body.name')))
find_user.run()

# 修改user，验证name与修改后一致
new_user = {"name": "Hermione2", "password": "123456789"}
modify_user = Api('patch', '/users/{id}', path_params={"id": login_user_id}, body=new_user)
modify_user.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.name'), '==', modify_user.get_variable('request.body.name')))
modify_user.run()

# 查询user，验证name已修改
find_user = Api('get', '/users/{id}', path_params={"id": login_user_id})
find_user.add_operation('post', lambda cur: assertion(cur.get_variable('response.body.data.name'), '==', modify_user.get_variable('request.body.name')))
find_user.run()

# 用原本账号login失败
login_user = Api('post', '/users/login', body=user, expected_status_code=401)
login_user.run()

# 用新账号login成功
login_user = Api('post', '/users/login', body=new_user, expected_status_code=200)
login_user.add_operation('post', lambda cur: set_global_variables("access_token", cur.get_variable('response.body.data.accessToken')))
login_user.run()

# 删除user
delete_user = Api('delete', '/users/{id}', path_params={"id": login_user_id})
delete_user.run()