import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from HYauth import models
from signUp import models as signUp_models
from HYauth.email import send_confirm_email

# Create your views here.

def login(request):
	try:
		studentId = request.session["studentId"]
		user = models.User.objects.get(studentId = studentId)
	except:
		user = None
	if user != None:
		messages.add_message(request, messages.INFO, '你已经登陆了啊:)')
		return redirect('/HYauth')
	if request.method == "POST":
		studentId = request.POST["studentId"]
		password = request.POST["password"]
		try:
			user = models.User.objects.get(studentId = studentId)
		except:
			messages.add_message(request, messages.INFO, '诶？这个学号好像不存在呀！')
			template = get_template('login.html')
			html = template.render(context = locals(), request = request)
			return HttpResponse(html)
		if user.verify_password(password):
			request.session["studentId"] = studentId
			return redirect('/HYauth')
		messages.add_message(request, messages.INFO, '密码好像有点不对啊！要不再检查一下吧。')
	template = get_template('login.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def logout(request):
	del request.session["studentId"]
	messages.add_message(request, messages.INFO, 'You have been logged out.')
	return redirect('/HYauth')
		
def index(request):	
	'''
	try:
		user = models.User.objects.get(studentId = request.session['studentId'])
		username = user.name
	except:
		user = None
	template = get_template('index.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	'''
	return redirect('/')
	
def register(request):
	#state = {
	#	'success': False,
	#	'message': ''
	#}
	try:
		studentId = request.session["studentId"]
		user = models.User.objects.get(studentId = studentId)
	except:
		user = None
	if user != None:
		messages.add_message(request, messages.INFO, '您已经登录啦！不用再注册了。')
		return redirect('/HYauth')
	if request.method == "POST":
		studentId = request.POST["studentId"]
		name = request.POST["name"]
		qq = request.POST["qq"]
		password = request.POST["password"]
		try:
			user = models.User.objects.get(studentId = studentId)
		except:
			user = None
		if user == None:
			role = None
			temp_email = qq + '@qq.com'
			if temp_email == settings.EMAIL_HOST_USER:
				print('in')
				role = models.Role.objects.filter(permissions = 0xff).first()
				print(role)
			if role is None:
				role = models.Role.objects.filter(default = True).first()
			user = models.User.objects.create(role = role, studentId = studentId, name = name, qq = qq)
			user.password_hash = user.get_password_hash(password)
			user.save()
			img = request.build_absolute_uri('/static/img/email_logo.png')
			token = user.generate_confirmation_token()
			url = request.build_absolute_uri(reverse('HYauth_confirm', args = {token}))
			#print(url)
			info = {
				'name': name,
				'url': url,
				'img': img,
			}
			to = []
			temp = qq + '@qq.com'
			to.append(temp)
			#print(os.getcwd())
			send_confirm_email('弘毅学堂信息平台激活账户', 'email/confirm.html', info, settings.EMAIL_HOST_USER, to)
			messages.add_message(request, messages.INFO, '你已经成功提交注册啦!快去你的QQ邮箱查看邮件激活账户吧!')
			request.session["studentId"] = studentId
			return redirect('/HYauth')
		else:
			messages.add_message(request, messages.INFO, '貌似你的学号已经被注册了欸!如果不是你本人操作，请联系管理员进行核查吧!')
	template = get_template('register.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def confirm(request, token):
	try:
		user = models.User.objects.get(studentId = request.session['studentId'])
	except:
		user = None
	if user == None:
		return redirect('/HYauth/login')
	if user.confirmed:
		return redirect('/HYauth')
	if user.confirm(token):
		messages.add_message(request, messages.SUCCESS, 'You have confirmed your account. Thanks!')
	else:
		messages.add_message(request, messages.INFO, 'The confirmation link is invalid or has expired.')
	return redirect('/HYauth')
	
def resend_confirmation(request):
	try:
		user = models.User.objects.get(studentId = request.session['studentId'])
	except:
		user = None
	if user == None:
		return redirect('/HYauth/login')
	if user.confirmed:
		return redirect('/HYauth')
	img = request.build_absolute_uri('/static/img/email_logo.png')
	token = user.generate_confirmation_token()
	url = request.build_absolute_uri(reverse('HYauth_confirm', args = {token}))
	#print(url)
	info = {
		'name': name,
		'url': url,
		'img': img,
	}
	to = []
	temp = qq + '@qq.com'
	to.append(temp)
	#print(os.getcwd())
	send_confirm_email('弘毅学堂信息平台激活账户', 'email/confirm.html', info, settings.EMAIL_HOST_USER, to)
	messages.add_message(request, messages.INFO, '我们又重新向你发送了一封邮件，快去你的QQ邮箱查看邮件激活账户吧!')
	return redirect('/HYauth')
	
def change_password(request):
	try:
		user = models.User.objects.get(studentId = request.session['studentId'])
	except:
		user = None
	if user == None:
		return redirect('/HYauth/login')
	if request.method == "POST":
		password = request.POST["newPassword"]
		user.password_hash = user.get_password_hash(password)
		user.save()
		messages.add_message(request, messages.INFO, '重置密码成功!')
		del request.session["studentId"]
		return redirect('/HYauth/login')
	current_user = user
	small_face = user.gravatar(request, size=32)
	template = get_template('user/change_password.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def user(request, studentId):
	try:
		current_user = models.User.objects.get(studentId = request.session['studentId'])
		current_user_info = {
			'studentId': current_user.studentId,
			'is_administrator': current_user.is_administrator(),
		}
		small_face = current_user.gravatar(request, size=32)
		#print(current_user.is_administrator())
		#print(current_user.role.permissions)
	except:
		current_user = None
	user = models.User.objects.filter(studentId = studentId).first()
	if user is None:
		raise Http404("User does not exist")
	signups = signUp_models.SignUp.objects.filter(user = user)
	infos = []
	for signup in signups:
		images = []
		for banner in signup.banner_set.all():
			images.append(banner.img)
		#if len(imgs) > 0:
		_info = {
			'id': signup.id,
			'user': signup.user,
			'title': signup.title,
			'content': signup.content,
			'timestamp': signup.timestamp,
			'deadline': signup.deadline,
			'imgs': images,
		}
		'''
		else:
			_info = {
				'user': signup.user,
				'title': signup.title,
				'content': signup.content,
				'timestamp': signup.timestamp,
				'deadline': signup.deadline,
			}
		'''
		infos.append(_info)
	#print(infos)
	face = user.gravatar(request, size=256)
	template = get_template('user/userinfo.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def edit_profile_admin(request, studentId):
	try:
		current_user = models.User.objects.get(studentId = request.session['studentId'])
		small_face = current_user.gravatar(request, size=32)
	except:
		current_user = None
	if current_user == None:
		return redirect('/HYauth/login')
	elif current_user.can(0x08) is not True:
		messages.add_message(request, messages.INFO, '对不起，您没有权限!')
		return redirect(request.build_absolute_uri(reverse('HYauth_user', args = {studentId})))
	try:
		user = models.User.objects.get(studentId = studentId)
	except:
		user = None
	if user == None:
		raise Http404("User does not exist")
	if request.method == "POST":
		phone = request.POST["phone"]
		location = request.POST["location"]
		department_position = int(request.POST["department_position"], 10)
		try:
			department1 = int(request.POST["department1"], 10)
		except:
			department1 = 0
		try:
			department2 = int(request.POST["department2"], 10)
		except:
			department2 = 0
		#print(department1)
		#print(type(department2))
		department = department1|department2
		try:
			major = int(request.POST["major"], 10)
		except:
			major = 0
		try:
			class_room = int(request.POST["class_room"], 10)
		except:
			class_room = 0
		about_me = request.POST["about_me"]
		user.phone = phone
		user.location = location
		user.department_position = department_position
		user.department = department
		user.major = major
		user.class_room = class_room
		user.about_me = about_me
		user.save()
		messages.add_message(request, messages.SUCCESS, '您已成功更新profile!')
		return redirect(request.build_absolute_uri(reverse('HYauth_user', args = {studentId})))
	face = user.gravatar(request, size=256)
	template = get_template('user/edit_profile.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def edit_profile(request):
	try:
		user = models.User.objects.get(studentId = request.session['studentId'])
	except:
		user = None
	if user == None:
		return redirect('/HYauth/login')
	if request.method == "POST":
		phone = request.POST["phone"]
		location = request.POST["location"]
		department_position = int(request.POST["department_position"], 10)
		try:
			department1 = int(request.POST["department1"], 10)
		except:
			department1 = 0
		try:
			department2 = int(request.POST["department2"], 10)
		except:
			department2 = 0
		if department_position == 0:
			department = 0
		elif department_position == 1 or department_position == 2:
			department = department1|department2
		else:
			department = department1
		try:
			major = int(request.POST["major"], 10)
		except:
			major = 0
		try:
			class_room = int(request.POST["class_room"], 10)
		except:
			class_room = 0
		about_me = request.POST["about_me"]
		user.phone = phone
		user.location = location
		user.department_position = department_position
		user.department = department
		user.major = major
		user.class_room = class_room
		user.about_me = about_me
		user.save()
		messages.add_message(request, messages.SUCCESS, '您已成功更新profile!')
		return redirect(request.build_absolute_uri(reverse('HYauth_user', args = {user.studentId})))
	current_user = user
	small_face = user.gravatar(request, size=32)
	face = user.gravatar(request, size=256)
	template = get_template('user/edit_profile.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)