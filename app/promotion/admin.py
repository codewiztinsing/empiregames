from django.contrib import admin
from .models import Promotion, Banner



class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title',)
    list_per_page = 10


class BannerAdmin(admin.ModelAdmin):
    list_display = ('image', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('image',)
    list_per_page = 10

admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Banner, BannerAdmin)