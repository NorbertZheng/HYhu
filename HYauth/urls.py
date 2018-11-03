"""HYhu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from HYauth import views 

urlpatterns = [
	url(r'^$', views.index, name = "HYauth_index"),
	url(r'^login$', views.login, name = "HYauth_login"),
	url(r'^logout$', views.logout, name = "HYauth_logout"),
	url(r'^register$', views.register, name = "HYauth_register"),
	url(r'^change-password$', views.change_password, name = "HYauth_change_password"),
	url(r'^confirm$', views.resend_confirmation, name = "HYauth_resend_confirmation"),
	url(r'^confirm/(?P<token>.+)/$', views.confirm, name = "HYauth_confirm"),
	url(r'^user/(?P<studentId>\d{13})$', views.user, name = "HYauth_user"),
	url(r'^edit/(?P<studentId>\d{13})$', views.edit_profile_admin, name = "HYauth_edit_admin"),
	url(r'^edit$', views.edit_profile, name = "HYauth_edit"),
]