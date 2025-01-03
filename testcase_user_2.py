from lib.api import Api
from lib.utils import set_global_variables, assertion

#
# 不可查看、修改或删除其他user的信息
#

# 创建user1
user_1 = {
    "name": "Hermione",
    "password": "12345678"
}
create_user_1 = Api('post', '/users', body=user_1)
create_user_1.run()
user_1_id = create_user_1.get_variable('response.body.data.id')

# 创建user2
user_2 = {
    "name": "Hermione2",
    "password": "123456789"
}
create_user_2 = Api('post', '/users', body=user_2)
create_user_2.run()
user_2_id = create_user_2.get_variable('response.body.data.id')

# 查询user1，401
query_user_1 = Api('get', '/users/{id}', path_params={'id': user_1_id}, expected_status_code=401)
query_user_1.run()

# 登录user1
login_user_1 = Api('post', '/users/login', body=user_1, expected_status_code=200)
login_user_1.add_operation('post', lambda cur: set_global_variables("access_token", cur.get_variable('response.body.data.accessToken')))
login_user_1.run()

# 查询user2，401
query_user_2 = Api('get', '/users/{id}', path_params={'id': user_2_id}, expected_status_code=401)
query_user_2.run()

# 修改user2，401
update_user_2 = Api('patch', '/users/{id}', path_params={'id': user_2_id}, body={
    "name": "Hermione",
    "password": "12345678"
}, expected_status_code=401)
update_user_2.run()

# 删除user1
delete_user_1 = Api('delete', '/users/{id}', path_params={'id': user_1_id})
delete_user_1.run()

# 登录user2
login_user_2 = Api('post', '/users/login', body=user_2, expected_status_code=200)
login_user_2.add_operation('post', lambda cur: set_global_variables("access_token", cur.get_variable('response.body.data.accessToken')))
login_user_2.run()

# 删除user2
delete_user_2 = Api('delete', '/users/{id}', path_params={'id': user_2_id})
delete_user_2.run()