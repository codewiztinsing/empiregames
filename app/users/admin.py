from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'telegram_id', 'referral_code')
    search_fields = ('username', 'email', 'phone', 'telegram_id')
    list_filter = ('is_active', 'is_staff')
    list_per_page = 10


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'telegram_id', 'referral_code')
    search_fields = ('username', 'email', 'phone', 'telegram_id')
    list_filter = ('is_active', 'is_staff')
    list_per_page = 10

admin.site.register(User, UserAdmin)