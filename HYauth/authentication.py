import sys
from HYauth import models

class PasswordAuthenticationBackend(object):
	
	def authenticate(studentId, password):
		print('studentId', studentId, file = sys.stderr)
		if not models.User.objects.filter(studentId = studentId).exists():
			print('抱歉啊...没有找到这个人欸', file = sys.stderr)
			return None
		user = models.User.objects.get(studentId = studentId)
		if user.password != password:
			print('账号密码有误', file = sys.stderr)
			return None
		print('got user', file = sys.stderr)
		return user