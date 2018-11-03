import hashlib
import django.utils.timezone as timezone
from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from django.conf import settings

# Create your models here.

class Permission:
	FOLLOW = 0x01
	COMMENT = 0x02
	WRITE_ARTICLES = 0x04
	MODERATE_COMMENTS = 0x08
	ADMINISTER = 0x80
	
class Role(models.Model):
	name = models.CharField(max_length = 64, unique = True)
	default = models.BooleanField(default = False)
	permissions = models.IntegerField()
	
	def __str__(self):
		return self.name
		
	def __init__(self, *args, **kwargs):													#初始化permission为0
		super(Role, self).__init__(*args, **kwargs)
		if self.permissions is None:
			self.permissions = 0x00
		
	def reset_permissions(self):
		self.permission = 0x00
		
	def has_permission(self, perm):
		return (self.permissions & perm) == perm
		
	def add_permission(self, perm):
		if not self.has_permission(perm):
			self.permissions += perm

	def remove_permission(self, perm):
		if self.has_permission(perm):
			self.permissions -= perm
			
	@staticmethod
	def insert_roles():
		roles = {
			'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES, True),
			'Moderator':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS, False),
			'Administrator':(0xff, False)
		}
		default_role = 'User'
		
		for r in roles:
			role = Role.objects.filter(name = r).first()
			if role is None:
				role = Role(name = r)
			role.reset_permissions()
			for perm in roles[r]:
				role.add_permission(perm)
			role.default = (role.name == default_role)
			role.save()
		
class Department:
	Network_Technology_Department = 0x00
	Literature_Art_Department = 0x01
	Secretariat = 0x02
	Study_Department = 0x04
	Organization_Department = 0x08
	Press_Publicity_Department = 0x10
	Physical_Education_Department = 0x20
	Practice_Outreach_Department = 0x40
	Community_Center = 0x80
	Life_Interests_Ministry = 0x100
	

class User(models.Model):
	name = models.CharField(max_length = 64, null = False)
	qq = models.CharField(max_length = 64, null = False)
	studentId = models.CharField(max_length = 64, unique = True, null = False)		#studentId = models.BigIntegerField(unique = True, null = False)
	password_hash = models.CharField(max_length = 128, null = False)
	confirmed = models.BooleanField(default = False)
	department = models.IntegerField(default = 0)		#0x01: 网络技术部 0x02: 文艺部 0x04: 秘书处 0x08: 学习部 0x10: 组织部 0x20: 新闻宣传部 0x40: 体育部 0x80: 实践外联部 0x100: 社团中心 0x200: 生活权益部 0x00: 没有加入部门
	department_position = models.IntegerField(default = 0)		#1: 主席 2: 副主席 3: 部长 4: 副部 5: 部委 0: 没有加入部门
	phone = models.CharField(max_length = 64, default = '')		#phone = models.IntegerField()
	major = models.IntegerField(default = 0)
	class_room = models.IntegerField(default = 0)
	location = models.CharField(max_length = 64, default = '')
	about_me = models.TextField(default = '')
	member_since = models.DateTimeField(default = timezone.now)
	last_seen = models.DateTimeField(default = timezone.now)
	avatar_hash = models.CharField(max_length = 32)
	role = models.ForeignKey(Role, on_delete = models.CASCADE, default = None)
	
	def __str__(self):
		return self.name
		
	def __init__(self, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)				
		if self.qq is not None and self.avatar_hash is None:
			print("I'm in")
			self.avatar_hash = hashlib.md5(self.qq.encode('utf-8')).hexdigest()
		
		
	def can(self, perm):
		return self.role is not None and self.role.has_permission(perm)
		
	def is_administrator(self):
		return self.can(Permission.ADMINISTER)
		
	def is_assisting_administrator(self):
		return self.can(Permission.MODERATE_COMMENTS)
		
	def get_password_hash(self, password):
		return generate_password_hash(password)
		
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
		
	def generate_confirmation_token(self, expiration =3600):
		s = Serializer(settings.SECRET_KEY, expiration)
		return s.dumps({'confirm': self.id}).decode('utf-8')
		
	def confirm(self, token):
		s = Serializer(settings.SECRET_KEY)
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		self.save()
		return True
		
	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id}).decode('utf-8')
		
	def reset_password(token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		user = User.query.get(data.get('reset'))
		if user is None:
			return False
		user.password = new_password
		db.session.add(user)
		db.session.commit()
		return True
		
	def gravatar(self, request, size =100, default = 'identicon', rating = 'g'):
		if request.is_secure:
			url = 'http://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = hashlib.md5(self.qq.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url =url, hash = hash, size = size, default =default, rating = rating)