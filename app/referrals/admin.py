from django.contrib import admin
from .models import ReferralBonus, ReferralWithdrawal, UserGameStats, ReferralSettings

@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ('user', 'from_user', 'generation', 'win_amount', 'bonus_percentage', 'bonus_amount', 'status', 'created_at')
    list_filter = ('generation', 'status', 'created_at')
    search_fields = ('user__username', 'from_user__username', 'user__phone', 'from_user__phone')
    readonly_fields = ('created_at',)
    list_per_page = 20

@admin.register(ReferralWithdrawal)
class ReferralWithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__phone')
    readonly_fields = ('created_at',)
    list_per_page = 20

@admin.register(UserGameStats)
class UserGameStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'games_played_today', 'games_played_this_week', 'total_games_played', 'total_winnings', 'total_referral_bonus')
    search_fields = ('user__username', 'user__phone')
    readonly_fields = ('last_game_date', 'last_week_reset')
    list_per_page = 20

@admin.register(ReferralSettings)
class ReferralSettingsAdmin(admin.ModelAdmin):
    list_display = ('first_generation_bonus', 'second_generation_bonus', 'minimum_withdrawal', 'daily_games_required', 'weekly_games_required', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not ReferralSettings.objects.exists()