from django.contrib import admin
from .models import Wallet, Transaction, ChapaSession

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)
    list_filter = ('user__is_active', 'user__is_staff')
    list_per_page = 10

admin.site.register(Wallet, WalletAdmin)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ( 'amount', 'type', 'status', 'created_at')

    list_filter = ('type', 'status')
    list_per_page = 10


class ChapaSessionAdmin(admin.ModelAdmin):
    list_display = ( 'amount', 'currency', 'email', 'first_name', 'last_name', 'phone_number', 'trx_ref', 'ref_id', 'callback_url', 'return_url', 'customization', 'status', 'created_at')
    list_filter = ('status',)
    list_per_page = 10

admin.site.register(Transaction, TransactionAdmin)  
admin.site.register(ChapaSession, ChapaSessionAdmin)