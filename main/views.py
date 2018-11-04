from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.http import HttpResponse
from HYauth import models as HYauth_models

# Create your views here.

def index(request):	
	try:
		current_user = HYauth_models.User.objects.get(studentId = request.session['studentId'])
		username = current_user.name
		small_face = current_user.gravatar(request, size=32)
	except:
		current_user = None
	template = get_template('index.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)
	
def about(request):
	try:
		current_user = HYauth_models.User.objects.get(studentId = request.session['studentId'])
		small_face = current_user.gravatar(request, size=32)
	except:
		current_user = None
	template = get_template('about.html')
	html = template.render(context = locals(), request = request)
	return HttpResponse(html)