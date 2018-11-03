from django.contrib import admin
from signUp import models

# Register your models here.

class SignUpAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'user', 'timestamp', 'deadline', 'enabled')				#, 'applicant')这里不能够显示ManyToManyField的数据
	ordering = ('deadline',)
	
class BannerAdmin(admin.ModelAdmin):
	list_display = ('signup', 'img')
	ordering = ('signup',)
	
#class SignUpUserAdmin(admin.ModelAdmin):
#	list_display = ('user', 'signUp', 'pushed_at')
#	ordering = ('pushed_at',)

admin.site.register(models.SignUp, SignUpAdmin)
admin.site.register(models.Banner, BannerAdmin)
#admin.site.register(models.SignUpUser, SignUpUserAdmin)