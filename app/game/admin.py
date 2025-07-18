from django.contrib import admin
from .models import Game

admin.site.site_header = "Wow Bingo Admin"
admin.site.site_title = "Wow Bingo Admin Portal"
admin.site.index_title = "Welcome to Wow Bingo Administration"


class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'started', 'ended')
    list_filter = ('started', 'ended')
    search_fields = ('id',)
    list_per_page = 10

admin.site.register(Game, GameAdmin)