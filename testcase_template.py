from lib.api import Api
from lib.utils import set_global_variables, assertion

#
# 
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


# 删除user
delete_user = Api('delete', '/users/{id}', path_params={"id": login_user_id})
delete_user.run()