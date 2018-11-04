import os
import time
import datetime
from PIL import Image
from django.conf import settings
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from HYauth import models as HYauth_models
from signUp import models

# Create your views here.

def index(request):
	try:
		current_user = HYauth_models.User.objects.get(studentId = request.session['studentId'])
		username = current_user.name
		small_face = current_user.gravatar(request, size=32)
	except:
		current_user = None
	signups = models.SignUp.objects.all()
	infos = []
	for signup in signups:
		images = []
		for banner in signup.banner_set.all():
			images.append(banner.img)
		_info = {
			'id': signup.id,
			'user': signup.user,
			'title': signup.title,
			'content': signup.content,
			'timestamp': signup.timestamp,
			'deadline': signup.deadline,
			'imgs': images,
		}
		infos.append(_info)
	template = get_template('signUp_index.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def new(request):
	try:
		current_user = HYauth_models.User.objects.get(studentId = request.session["studentId"])
	except:
		current_user = None
	if current_user == None:
		messages.add_message(request, messages.INFO, '请先登录，才能发布报名哦.')
		return redirect('/')
	elif current_user.can(0x08) is not True:
		messages.add_message(request, messages.INFO, '对不起，您没有权限!')
		return redirect(request.build_absolute_uri(reverse('HYauth_user', args = {current_user.studentId})))
	if request.method == "POST":
		title = request.POST["title"]
		enddate = request.POST["enddate"]
		endtime = request.POST["endtime"]
		backgroundImgUrls = request.FILES.getlist('backgroundImgUrls', None)
		content = request.POST["content"]
		signup = models.SignUp.objects.create(title = title, user = current_user.name, content = content)
		temp_time = enddate + " " + endtime + ":00"
		temp_timestamp = string_toDatetime(temp_time)
		signup.deadline = temp_timestamp
		signup.save()
		if backgroundImgUrls:
			for backgroundImgUrl in backgroundImgUrls:
				try:
					_upload_state = upload_img(backgroundImgUrl)
					if _upload_state['success']:
						banner = models.Banner(signup = signup, img = _upload_state['message'])
						banner.save()
					else:
						messages.add_message(request, messages.INFO, _upload_state['message'] + '上传失败')
				except:
					messages.add_message(request, messages.INFO, '这个只能上传图片呀.')
		messages.add_message(request, messages.INFO, '报名成功发布啦!')
		return redirect(request.build_absolute_uri(reverse('HYauth_user', args = {current_user.studentId})))
	small_face = current_user.gravatar(request, size=32)
	face = current_user.gravatar(request, size=256)
	template = get_template('signUp_new.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def detail(request, id):
	try:
		signup = models.SignUp.objects.get(id = id)
	except:
		signup = None
	if signup == None:
		messages.add_message(request, messages.INFO, '此报名不存在.')
		return redirect('/signUp')
	try:
		current_user = HYauth_models.User.objects.get(studentId = request.session['studentId'])
		small_face = current_user.gravatar(request, size=32)
		is_signUper = signup.user_is_signUper(current_user.studentId)
	except:
		current_user = None
	try:
		user = HYauth_models.User.objects.filter(name = signup.user).first()
		face = user.gravatar(request, size=256)
	except:
		user = None
	users = signup.get_all_signUpers
	template = get_template('signUp_detail.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def signup(request, id):
	try:
		signup = models.SignUp.objects.get(id = id)
	except:
		signup = None
	if signup == None:
		messages.add_message(request, messages.INFO, '此报名不存在.')
		return redirect('/signUp')
	try:
		current_user = HYauth_models.User.objects.get(studentId = request.session["studentId"])
	except:
		current_user = None
	if current_user == None:
		messages.add_message(request, messages.INFO, '请先登录再报名哦!')
		return redirect('/HYauth/login')
	if current_user.class_room == 0 or current_user.major == 0:
		messages.add_message(request, messages.INFO, '请先补全专业班级信息再报名哦!')
		return redirect(request.build_absolute_uri(reverse('HYauth_user', args = {current_user.studentId})))
	if signup.user_is_signUper(current_user.studentId):
		messages.add_message(request, messages.INFO, '你已经报名了哦.')
		return redirect(request.build_absolute_uri(reverse('signUp_detail', args = {id})))
	signup.user_join_signUpers(current_user.studentId)
	messages.add_message(request, messages.INFO, '报名成功啦!')
	return redirect(request.build_absolute_uri(reverse('signUp_detail', args = {id})))
	
def cancel_signup(request, id):
	try:
		signup = models.SignUp.objects.get(id = id)
	except:
		signup = None
	if signup == None:
		messages.add_message(request, messages.INFO, '此报名不存在.')
		return redirect('/signUp')
	try:
		current_user = HYauth_models.User.objects.get(studentId = request.session["studentId"])
	except:
		current_user = None
	if current_user == None:
		messages.add_message(request, messages.INFO, '请先登录再取消报名哦!')
		return redirect('/HYauth/login')
	if not signup.user_is_signUper(current_user.studentId):
		messages.add_message(request, messages.INFO, '你还没有报名哦.')
		return redirect(request.build_absolute_uri(reverse('signUp_detail', args = {id})))
	signup.user_remove_from_signUpers(current_user.studentId)
	messages.add_message(request, messages.INFO, '成功取消报名!')
	return redirect(request.build_absolute_uri(reverse('signUp_detail', args = {id})))
	
	
def upload_img(data):
	_state = {
		'success': False,
		'message': '',
	}
	
	if data.size > 0:
		base_im = Image.open(data)
		
		file_name = '.'.join(data.name.split('.')[:-1]) + time.strftime('%H%M%S') + '.png'
		file_root_path = '%s/' % (settings.MEDIA_ROOT)
		file_sub_path = 'signUp/background/' + '%s' % (str(time.strftime("%Y/%m/%d/")))
		
		file_path = os.path.abspath(file_root_path + file_sub_path)
		im = base_im
		im = make_thumb(im, 292, 400)
		#im = make_thumb2(im)
		if not os.path.exists(file_path):
			os.makedirs(file_path)
		im.save('%s/%s' % (file_path, file_name), 'PNG')
		
		_state['success'] = True
		_state['message'] = file_sub_path + file_name
	else:
		_state['success'] = False
		_state['message'] = 'Failed to save img.'
		
	return _state
	
def make_thumb(im, width_size = 100, height_size = 100):
	width, height = im.size
	
	if width == height:
		region = im
	else:
		if width > height:
			delta = (width - height) / 2
			box = (delta, 0, delta + height, height)
		else:
			delta = (height - width) / 2
			box = (0, delta, width, delta + width)
		region = im.crop(box)
		
	thumb = region.resize((width_size, height_size), Image.ANTIALIAS)
	return thumb
	
def make_thumb2(im):
	width, height = im.size
	region = im
		
	thumb = region.resize((width, height), Image.ANTIALIAS)
	return thumb
	
def string_toTimestamp(str):
    return time.mktime(time.strptime(str, "%Y-%m-%d %H:%M:%S"))
	
def string_toDatetime(str):
    return datetime.datetime.strptime(str, "%Y-%m-%d %H:%M:%S")