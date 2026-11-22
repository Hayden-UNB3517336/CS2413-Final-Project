from locust import HttpUser, task, between

class LoginUser(HttpUser):
	# This sets the wait time between each login instance; since both parameters are set to 0, the wait time will be almost instant.
	wait_time = between(0, 0)

	@task
	def login(self):
		self.client.post(
			"/rest/user/login",
			json={"email": "test@test.com", "password": "password123"},
			name="POST /rest/user/login"
		)