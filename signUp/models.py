import django.utils.timezone as timezone
from django.db import models
from HYauth import models as HYauth_models

# Create your models here.

class SignUp(models.Model):
	title = models.CharField(max_length = 64, null = False)
	timestamp = models.DateTimeField(default = timezone.now)
	deadline = models.DateTimeField(default = timezone.now)
	content = models.TextField()
	enabled = models.BooleanField(default = False)
	user = models.CharField(max_length = 64, null = False)
	applicants = models.ManyToManyField(HYauth_models.User)
	
	def __str__(self):
		return self.title
		
	def __init__(self, *args, **kwargs):													
		super(SignUp, self).__init__(*args, **kwargs)
		
	def user_is_signUper(self, studentId):
		try:
			user = self.applicants.get(studentId = studentId)
		except:
			user = None
		if user == None:
			return False
		return True
		
	def user_join_signUpers(self, studentId):
		try:
			user = HYauth_models.User.objects.get(studentId = studentId)
		except:
			return False
		self.applicants.add(user)
		return True
		
	def user_remove_from_signUpers(self, studentId):
		try:
			user = HYauth_models.User.objects.get(studentId = studentId)
		except:
			return False
		self.applicants.remove(user)
		return True
		
	def get_all_signUpers(self):
		return self.applicants.all()

class Banner(models.Model):
	id = models.AutoField(primary_key=True)
	img = models.ImageField(upload_to = 'signUp/background/%Y/%m/%d', default = '', blank = True)
	signup = models.ForeignKey(SignUp, on_delete = models.CASCADE, related_name = "banner_set")
	
	def __str__(self):
		return "%s, %s" % (self.signup.title, self.img)