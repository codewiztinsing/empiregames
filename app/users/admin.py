from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'phone', 'telegram_id')
    search_fields = ('username', 'phone', 'telegram_id')
    list_filter = ('is_active', 'is_staff')
    list_per_page = 10


class UserAdmin(admin.ModelAdmin):
    list_display = ("id",'username', 'phone', 'telegram_id')
    search_fields = ('username', 'phone', 'telegram_id')
    list_filter = ('is_active', 'is_staff')
    list_per_page = 10

admin.site.register(User, UserAdmin)