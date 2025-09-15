from django.contrib import admin
from .models import Game,PlayerGame,GameSettings,GameType
from wallet.models import ManualSession

admin.site.site_header = "Wow Bingo Admin"
admin.site.site_title = "Wow Bingo Admin Portal"
admin.site.index_title = "Welcome to Wow Bingo Administration"


class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'started', 'ended', 'status', 'winner')
    list_filter = ('started', 'ended')
    search_fields = ('id',)
    list_per_page = 10



admin.site.register(Game, GameAdmin)

class PlayerGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game', 'has_bingo')
    list_filter = ('has_bingo',)
    search_fields = ('id', 'user__username', 'game__entry_fee', 'game__status', 'game__winner', 'game__players')
    list_per_page = 10


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

    
    list_filter = ('status',)
    search_fields = ('id', 'session_id', 'amount', 'status', 'phone_number')
    list_per_page = 10


class GameTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'bet_amount', 'commission')
    list_filter = ('bet_amount', 'commission')
    search_fields = ('id', 'bet_amount', 'commission')
    list_per_page = 10

admin.site.register(PlayerGame, PlayerGameAdmin)
admin.site.register(GameSettings, GameSettingsAdmin)
admin.site.register(ManualSession, ManualSessionAdmin)
admin.site.register(GameType, GameTypeAdmin)
