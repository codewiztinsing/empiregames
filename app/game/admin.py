from django.contrib import admin
from .models import Game, GameRoom, PlayerGame, GameSettings, FakePlayerSettings, CustomBingoCard
from wallet.models import ManualSession

admin.site.site_header = "Wow Bingo Admin"
admin.site.site_title = "Wow Bingo Admin Portal"
admin.site.index_title = "Welcome to Wow Bingo Administration"


class GameAdmin(admin.ModelAdmin):
    list_display = ('game_number', 'room', 'status', 'total_players', 'real_players', 'fake_players', 'prize_pool', 'created_at', 'get_winner_display')
    list_filter = ('status', 'room', 'total_players', 'real_players', 'fake_players', 'winner')
    search_fields = ('game_number', 'winner__username', 'winner__telegram_id')
    list_per_page = 10


class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'entry_fee', 'currency', 'max_players', 'is_active', 'created_at')
    list_filter = ('room_type', 'is_active', 'currency')
    search_fields = ('name', 'entry_fee')
    list_editable = ('is_active',)
    list_per_page = 10


class PlayerGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'card_number', 'entry_fee', 'is_winner', 'win_amount', 'joined_at')
    list_filter = ('is_winner', 'game__status', 'game__room')
    search_fields = ('user__username', 'user__telegram_id', 'card_number')
    list_per_page = 10


class GameSettingsAdmin(admin.ModelAdmin):
    list_display = ('default_countdown_duration', 'default_game_speed', 'max_fake_players', 'fake_player_threshold')
    list_filter = ('default_game_speed', 'fake_players_can_win')
    search_fields = ('default_countdown_duration',)
    list_per_page = 10


class ManualSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_id', 'amount', 'status', 'phone_number')
    list_filter = ('status',)
    search_fields = ('id', 'session_id', 'amount', 'status', 'phone_number')
    list_per_page = 10


class FakePlayerSettingsAdmin(admin.ModelAdmin):
    list_display = ('max_fake_players', 'calls_before_fake_winner', 'real_players_threshold', 'fake_players_can_win', 'updated_at')
    list_editable = ('max_fake_players', 'calls_before_fake_winner', 'real_players_threshold', 'fake_players_can_win')
    list_display_links = ('updated_at',)  # Set a non-editable field as link
    list_filter = ('fake_players_can_win',)
    search_fields = ('max_fake_players', 'calls_before_fake_winner')
    list_per_page = 10

    def has_add_permission(self, request):
        # Allow adding new instances for different tenants
        return True

    def has_delete_permission(self, request, obj=None):
        # Allow deletion
        return True


class CustomBingoCardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'is_default', 'created_at', 'updated_at')
    list_filter = ('is_default', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__telegram_id', 'name')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Card Information', {
            'fields': ('user', 'name', 'is_default')
        }),
        ('Card Numbers', {
            'fields': ('numbers',),
            'description': 'Bingo card numbers organized by column (B, I, N, G, O)'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['set_as_default', 'unset_default']
    
    def set_as_default(self, request, queryset):
        """Set selected cards as default for their users"""
        updated_count = 0
        for card in queryset:
            CustomBingoCard.set_default_card(card.user, card.id)
            updated_count += 1
        self.message_user(request, f"{updated_count} cards set as default successfully.")
    set_as_default.short_description = "Set as default card"
    
    def unset_default(self, request, queryset):
        """Unset default status for selected cards"""
        updated = queryset.filter(is_default=True).update(is_default=False)
        self.message_user(request, f"{updated} cards unset as default.")
    unset_default.short_description = "Unset default status"


admin.site.register(Game, GameAdmin)
admin.site.register(GameRoom, GameRoomAdmin)
admin.site.register(PlayerGame, PlayerGameAdmin)
admin.site.register(GameSettings, GameSettingsAdmin)
admin.site.register(FakePlayerSettings, FakePlayerSettingsAdmin)
admin.site.register(CustomBingoCard, CustomBingoCardAdmin)
# ManualSession is registered in wallet.admin
