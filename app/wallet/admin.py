from django.contrib import admin
from .models import Wallet, Transaction, ChapaSession

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance','created_at','user__phone','user__telegram_id')
    search_fields = ('user__username',"user__telegram_id","user__phone")
    list_filter = ('user__is_active', 'user__is_staff')
    list_per_page = 10

admin.site.register(Wallet, WalletAdmin)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user__username", 'amount', 'type', 'status', 'reference',"user__phone","user__telegram_id","created_at")
    search_fields = ('user__phone', 'user__telegram_id','user__username',"created_at")
    ordering = ('-created_at',)
    list_display_links = ('reference',)

    list_filter = ('type', 'status','user__phone','user__telegram_id','created_at')
    list_per_page = 10


class ChapaSessionAdmin(admin.ModelAdmin):
    list_display = ( 'amount', 'currency', 'email', 'first_name', 'last_name', 'phone_number', 'tx_ref', 'ref_id', 'callback_url', 'return_url', 'customization', 'status', 'created_at')
    ordering = ('-created_at',)
    list_display_links = ('tx_ref',)
    list_filter = ('status','created_at')
    search_fields = ('user__phone', 'user__telegram_id','user__username')
    list_per_page = 10

admin.site.register(Transaction, TransactionAdmin)  
admin.site.register(ChapaSession, ChapaSessionAdmin)