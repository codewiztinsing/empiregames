from django.contrib import admin
from .models import Promotion, Banner, Campaign, PromotionTracking


class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'promotion_type', 'status', 'view_count', 'click_count', 'created_at')
    list_filter = ('status', 'promotion_type', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('status',)
    list_per_page = 10


class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'display_order', 'target_audience', 'created_at')
    list_filter = ('is_active', 'target_audience', 'created_at')
    search_fields = ('name',)
    list_editable = ('is_active', 'display_order')
    list_per_page = 10


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'total_views', 'total_clicks', 'total_conversions', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('status',)
    list_per_page = 10


class PromotionTrackingAdmin(admin.ModelAdmin):
    list_display = ('promotion', 'user', 'action_type', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('promotion__title', 'user__username', 'user__telegram_id')
    list_per_page = 10


admin.site.register(Promotion, PromotionAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(PromotionTracking, PromotionTrackingAdmin)