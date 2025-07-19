from django.contrib import admin
from .models import Game

admin.site.site_header = "Wow Bingo Admin"
admin.site.site_title = "Wow Bingo Admin Portal"
admin.site.index_title = "Welcome to Wow Bingo Administration"


class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'started', 'ended','telegram_id')
    list_filter = ('started', 'ended','telegram_id')
    search_fields = ('id',)
    list_per_page = 10

admin.site.register(Game, GameAdmin)