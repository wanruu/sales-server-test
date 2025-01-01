
from api_step import ApiStep


# step = ApiStep('post', '/users/login', body={'name':'hello world', 'password': '12345678'})
# step.expect(200)
# step.run()


step = ApiStep('post', '/users', body={'name':'hello world', 'password': '12345678'})
step.expect(201)
step.run()