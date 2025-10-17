from django.contrib import admin
from .models import Game,GameSettings,GameType,FakePlayerSettings
from wallet.models import ManualSession

admin.site.site_header = "Wow Bingo Admin"
admin.site.site_title = "Wow Bingo Admin Portal"
admin.site.index_title = "Welcome to Wow Bingo Administration"


class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'total_players', 'real_players', 'fake_players', 'total_win_amount', 'status', 'ended', 'get_winner_display')
    list_filter = ( 'total_players', 'real_players', 'fake_players', 'total_win_amount', 'status', 'ended', 'winner')
    search_fields = ('id', 'winner__username', 'winner__telegram_id')
    list_per_page = 10



admin.site.register(Game, GameAdmin)



class GameSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'game_speed', 'count_down_time')
    list_filter = ('game_speed', 'count_down_time')
    search_fields = ('id',)
    list_per_page = 10


class ManualSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_id', 'amount', 'status', 'phone_number')
    list_filter = ('status',)
    search_fields = ('id', 'session_id', 'amount', 'status', 'phone_number')
    list_per_page = 10


class GameTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'bet_amount', 'commission')
    list_filter = ('bet_amount', 'commission')
    search_fields = ('id', 'bet_amount', 'commission')
    list_per_page = 10

admin.site.register(GameSettings, GameSettingsAdmin)
# ManualSession is registered in wallet.admin
admin.site.register(GameType, GameTypeAdmin)


class FakePlayerSettingsAdmin(admin.ModelAdmin):
    list_display = ('max_fake_players', 'calls_before_fake_winner', 'fake_players_can_win', 'updated_at')
    list_editable = ('max_fake_players', 'calls_before_fake_winner', 'fake_players_can_win')
    list_display_links = ('updated_at',)  # Set a non-editable field as link
    list_filter = ('fake_players_can_win',)
    search_fields = ('max_fake_players', 'calls_before_fake_winner')
    list_per_page = 10

    def has_add_permission(self, request):
        # Only allow one instance
        return not FakePlayerSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of the only instance
        return False


admin.site.register(FakePlayerSettings, FakePlayerSettingsAdmin)
