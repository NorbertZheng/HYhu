from django.contrib import admin
from signUp import models

# Register your models here.

class SignUpAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'user', 'timestamp', 'deadline', 'enabled')
	ordering = ('deadline',)
	
class BannerAdmin(admin.ModelAdmin):
	list_display = ('signup', 'img')
	ordering = ('signup',)
	

admin.site.register(models.SignUp, SignUpAdmin)
admin.site.register(models.Banner, BannerAdmin)