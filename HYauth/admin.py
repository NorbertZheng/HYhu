from django.contrib import admin
from HYauth import models

# Register your models here.

class RoleAdmin(admin.ModelAdmin):
	list_display = ('name', 'permissions')
	ordering = ('permissions', )
	
class UserAdmin(admin.ModelAdmin):
	list_display = ('name', 'role')

admin.site.register(models.Role, RoleAdmin)
admin.site.register(models.User, UserAdmin)