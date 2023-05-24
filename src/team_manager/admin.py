from django.contrib import admin

from team_manager.models import User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
