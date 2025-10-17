from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, SupportUser, ReferralBonus, ReferralAnnouncement
from .referral_services import ReferralService


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'phone', 'telegram_id', 'referral_code', 'referred_by', 'is_agent', 'total_referral_earnings', 'total_games_played', 'created_at']
    list_filter = ['is_agent', 'is_active', 'created_at']
    search_fields = ['username', 'phone', 'telegram_id', 'referral_code']
    readonly_fields = ['referral_code', 'created_at', 'updated_at']
    list_per_page = 10
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'phone', 'telegram_id', 'email', 'first_name', 'last_name')
        }),
        ('Referral Information', {
            'fields': ('referral_code', 'referred_by', 'is_agent', 'sponsor_changed', 'total_referral_earnings')
        }),
        ('Game Statistics', {
            'fields': ('total_games_played', 'games_played_today', 'games_played_this_week', 'last_game_date', 'last_week_reset')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        })
    )


class SupportUserAdmin(admin.ModelAdmin):
    list_display = ["id", 'user', 'role']
    search_fields = ('user', 'role')
    list_filter = ('role',)
    list_per_page = 10


class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ['id', 'referrer', 'winner', 'win_amount', 'bonus_type', 'bonus_amount', 'generation_level', 'status', 'created_at']
    list_filter = ['bonus_type', 'status', 'generation_level', 'created_at']
    search_fields = ['referrer__username', 'winner__username', 'game_id']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_bonuses', 'reject_bonuses']
    
    def approve_bonuses(self, request, queryset):
        approved_count = 0
        for bonus in queryset.filter(status='pending'):
            success, message = ReferralService.approve_bonus(bonus.id, request.user)
            if success:
                approved_count += 1
        self.message_user(request, f"{approved_count} bonuses approved successfully.")
    approve_bonuses.short_description = "Approve selected bonuses"
    
    def reject_bonuses(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"{updated} bonuses rejected.")
    reject_bonuses.short_description = "Reject selected bonuses"



class ReferralAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new announcement
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
admin.site.register(SupportUser, SupportUserAdmin)
admin.site.register(ReferralBonus, ReferralBonusAdmin)
admin.site.register(ReferralAnnouncement, ReferralAnnouncementAdmin)