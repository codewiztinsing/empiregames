from django.contrib import admin
from .models import (Wallet, 
            Transaction,
            ChapaSession,
            AddisPaySession,
            ManualSession,
            WithdrawalRequest
            )

class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance','created_at','get_user_phone','get_user_telegram_id')
    search_fields = ('user__username',"user__telegram_id","user__phone")
    list_filter = ('user__is_active', 'user__is_staff')
    list_per_page = 10
    
    def get_user_phone(self, obj):
        return obj.user.phone
    get_user_phone.short_description = 'Phone'
    get_user_phone.admin_order_field = 'user__phone'
    
    def get_user_telegram_id(self, obj):
        return obj.user.telegram_id
    get_user_telegram_id.short_description = 'Telegram ID'
    get_user_telegram_id.admin_order_field = 'user__telegram_id'

admin.site.register(Wallet, WalletAdmin)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ("get_user_username", 'amount', 'type', 'status', 'reference',"get_user_phone","get_user_telegram_id","created_at")
    search_fields = ('user__phone', 'user__telegram_id','user__username',"created_at")
    ordering = ('-created_at',)
    list_display_links = ('reference',)

    list_filter = ('type', 'status','user__phone','user__telegram_id','created_at')
    list_per_page = 10
    
    def get_user_username(self, obj):
        return obj.user.username
    get_user_username.short_description = 'Username'
    get_user_username.admin_order_field = 'user__username'
    
    def get_user_phone(self, obj):
        return obj.user.phone
    get_user_phone.short_description = 'Phone'
    get_user_phone.admin_order_field = 'user__phone'
    
    def get_user_telegram_id(self, obj):
        return obj.user.telegram_id
    get_user_telegram_id.short_description = 'Telegram ID'
    get_user_telegram_id.admin_order_field = 'user__telegram_id'


class ChapaSessionAdmin(admin.ModelAdmin):
    list_display = ( 'amount', 'currency','first_name','phone_number', 'status', 'created_at')
    ordering = ('-created_at',)
    list_display_links = ("phone_number","status","created_at","amount","currency","first_name")
   
    search_fields = ( 'first_name','phone_number','status','created_at','amount','currency')
    list_per_page = 10


class AddisPaySessionAdmin(admin.ModelAdmin):
    list_display = ( 'amount', 'currency','first_name','phone_number', 'status', 'created_at')
    ordering = ('-created_at',)
    list_display_links = ("phone_number","status","created_at","amount","currency","first_name")
   
    search_fields = ('first_name','phone_number','status','created_at','amount','currency')
    list_per_page = 10
    list_filter = ('status','created_at')


class ManualSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'phone_number', 'amount', 'transaction_number', 'status')
    search_fields = ('session_id', 'phone_number', 'transaction_number')
    list_filter = ('status',)
    list_per_page = 10


class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'created_at')
    search_fields = ('user', 'amount', 'status')
    list_filter = ('status',)
    list_per_page = 10


admin.site.register(Transaction, TransactionAdmin)  
admin.site.register(ChapaSession, ChapaSessionAdmin)
admin.site.register(AddisPaySession, AddisPaySessionAdmin)
admin.site.register(WithdrawalRequest, WithdrawalRequestAdmin)