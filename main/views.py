from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.http import HttpResponse
from HYauth import models as HYauth_models

# Create your views here.

def index(request):	
	try:
		user = HYauth_models.User.objects.get(studentId = request.session['studentId'])
		username = user.name
		small_face = user.gravatar(request, size=32)
	except:
		user = None
	#print(user)
	current_user = user
	template = get_template('index.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)