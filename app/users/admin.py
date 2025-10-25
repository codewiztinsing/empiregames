from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, SupportUser, WithdrawalRequest, ReferralAnnouncement, TelegramUser, Agent
# Referral services removed


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
            'fields': ('referral_code', 'referred_by', 'is_agent', 'total_referral_earnings')
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




class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'status', 'created_at', 'processed_by', 'processed_at']
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = ['user__username', 'user__phone']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_withdrawals', 'reject_withdrawals']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'amount', 'status')
        }),
        ('Processing', {
            'fields': ('processed_by', 'processed_at', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def approve_withdrawals(self, request, queryset):
        approved_count = 0
        for withdrawal in queryset.filter(status='pending'):
            withdrawal.status = 'approved'
            withdrawal.processed_by = request.user
            withdrawal.processed_at = timezone.now()
            withdrawal.save()
            approved_count += 1
        self.message_user(request, f"{approved_count} withdrawals approved successfully.")
    approve_withdrawals.short_description = "Approve selected withdrawals"
    
    def reject_withdrawals(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            processed_by=request.user,
            processed_at=timezone.now()
        )
        self.message_user(request, f"{updated} withdrawals rejected.")
    reject_withdrawals.short_description = "Reject selected withdrawals"



class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'display_name', 'username', 'first_name', 'last_name', 'is_bot', 'is_premium', 'linked_user', 'is_active', 'created_at']
    list_filter = ['is_bot', 'is_premium', 'is_verified', 'is_active', 'is_deleted', 'created_at']
    search_fields = ['telegram_id', 'username', 'first_name', 'last_name', 'phone_number']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at', 'last_seen']
    list_per_page = 20
    
    fieldsets = (
        ('Telegram Information', {
            'fields': ('telegram_id', 'username', 'first_name', 'last_name', 'language_code')
        }),
        ('Telegram Status', {
            'fields': ('is_bot', 'is_premium', 'is_verified')
        }),
        ('Profile Information', {
            'fields': ('photo_url', 'phone_number')
        }),
        ('Account Linking', {
            'fields': ('linked_user',)
        }),
        ('Status & Metadata', {
            'fields': ('is_active', 'is_deleted', 'deleted_at', 'last_seen', 'created_at', 'updated_at')
        })
    )
    
    def display_name(self, obj):
        """Display the best available name for the Telegram user"""
        return obj.display_name
    display_name.short_description = 'Display Name'
    
    actions = ['activate_users', 'deactivate_users', 'soft_delete_users']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True, is_deleted=False, deleted_at=None)
        self.message_user(request, f"{updated} Telegram users activated.")
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} Telegram users deactivated.")
    deactivate_users.short_description = "Deactivate selected users"
    
    def soft_delete_users(self, request, queryset):
        count = 0
        for user in queryset:
            user.soft_delete()
            count += 1
        self.message_user(request, f"{count} Telegram users soft deleted.")
    soft_delete_users.short_description = "Soft delete selected users"


class AgentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'referral_code', 'total_referrals', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__phone', 'user__telegram_id', 'referral_code']
    readonly_fields = ['referral_code', 'created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Agent Information', {
            'fields': ('user', 'referral_code')
        }),
        ('Statistics', {
            'fields': ('total_referrals',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def total_referrals(self, obj):
        """Display total number of referrals"""
        return User.objects.filter(referred_by=obj.user).count()
    total_referrals.short_description = 'Total Referrals'
    
    actions = ['view_referrals']
    
    def view_referrals(self, request, queryset):
        """View referrals for selected agents"""
        for agent in queryset:
            referrals = User.objects.filter(referred_by=agent.user)
            self.message_user(request, f"Agent {agent.user.username} has {referrals.count()} referrals")
    view_referrals.short_description = "View referrals for selected agents"


admin.site.register(User, UserAdmin)
admin.site.register(SupportUser, SupportUserAdmin)
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)
admin.site.register(TelegramUser, TelegramUserAdmin)
admin.site.register(Agent, AgentAdmin)
