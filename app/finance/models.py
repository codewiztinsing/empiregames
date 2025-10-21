from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Account(models.Model):
    """
    Unified account system for all financial operations
    """
    ACCOUNT_TYPES = [
        ('user_wallet', 'User Wallet'),
        ('house_account', 'House Account'),
        ('referral_pool', 'Referral Pool'),
        ('bonus_pool', 'Bonus Pool'),
        ('withdrawal_pool', 'Withdrawal Pool'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='accounts')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True, related_name='accounts')
    
    # Account details
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Balance information
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    currency = models.CharField(max_length=3, default='ETB')
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_frozen = models.BooleanField(default=False)
    freeze_reason = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
        unique_together = ['tenant', 'user', 'account_type']
        indexes = [
            models.Index(fields=['tenant', 'account_type']),
            models.Index(fields=['user', 'account_type']),
            models.Index(fields=['is_active', 'is_deleted']),
        ]
    
    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.get_account_type_display()}"
        return f"{self.tenant.name} - {self.get_account_type_display()}"
    
    def soft_delete(self):
        """Soft delete the account"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def freeze(self, reason=None):
        """Freeze the account"""
        self.is_frozen = True
        self.freeze_reason = reason
        self.save()
    
    def unfreeze(self):
        """Unfreeze the account"""
        self.is_frozen = False
        self.freeze_reason = None
        self.save()
    
    def can_transact(self):
        """Check if account can perform transactions"""
        return self.is_active and not self.is_frozen and not self.is_deleted


class Transaction(models.Model):
    """
    Enhanced transaction system with double-entry bookkeeping
    """
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('bet', 'Bet'),
        ('win', 'Win'),
        ('referral_bonus', 'Referral Bonus'),
        ('signup_bonus', 'Signup Bonus'),
        ('admin_adjustment', 'Admin Adjustment'),
        ('refund', 'Refund'),
        ('fee', 'Fee'),
        ('transfer', 'Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('reversed', 'Reversed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Double-entry bookkeeping
    debit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='debit_transactions')
    credit_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='credit_transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='ETB')
    
    # Reference information
    reference = models.CharField(max_length=100, blank=True, null=True)
    external_reference = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Related entities
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    game = models.ForeignKey('game.Game', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    
    # Processing information
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_transactions')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['tenant', 'transaction_type']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['reference']),
            models.Index(fields=['external_reference']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} {self.currency} - {self.get_status_display()}"
    
    def soft_delete(self):
        """Soft delete the transaction"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def process(self, processed_by=None):
        """Process the transaction"""
        if self.status != 'pending':
            raise ValueError("Only pending transactions can be processed")
        
        # Update account balances
        self.debit_account.balance -= self.amount
        self.credit_account.balance += self.amount
        
        self.debit_account.save()
        self.credit_account.save()
        
        # Update transaction status
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.processed_by = processed_by
        self.save()
    
    def reverse(self, reversed_by=None):
        """Reverse the transaction"""
        if self.status != 'completed':
            raise ValueError("Only completed transactions can be reversed")
        
        # Reverse account balances
        self.debit_account.balance += self.amount
        self.credit_account.balance -= self.amount
        
        self.debit_account.save()
        self.credit_account.save()
        
        # Update transaction status
        self.status = 'reversed'
        self.processed_at = timezone.now()
        self.processed_by = reversed_by
        self.save()


class Balance(models.Model):
    """
    Snapshot of account balances for reporting and reconciliation
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='balance_snapshots')
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')
    
    # Snapshot metadata
    snapshot_date = models.DateTimeField(auto_now_add=True)
    transaction_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-snapshot_date']
        verbose_name = 'Balance Snapshot'
        verbose_name_plural = 'Balance Snapshots'
        indexes = [
            models.Index(fields=['account', 'snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.account} - {self.balance} {self.currency} at {self.snapshot_date}"


class WithdrawalRequest(models.Model):
    """
    Enhanced withdrawal request system
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('crypto', 'Cryptocurrency'),
        ('cash', 'Cash'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='withdrawal_requests')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='finance_withdrawal_requests')
    
    # Withdrawal details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='ETB')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    # Payment information
    account_number = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=200, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Approval workflow
    approved_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_withdrawals')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Transaction reference
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Withdrawal Request'
        verbose_name_plural = 'Withdrawal Requests'
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} - {self.get_status_display()}"
    
    def approve(self, approved_by):
        """Approve the withdrawal request"""
        if self.status != 'pending':
            raise ValueError("Only pending withdrawals can be approved")
        
        self.status = 'approved'
        self.approved_by = approved_by
        self.approved_at = timezone.now()
        self.save()
    
    def reject(self, reason, rejected_by):
        """Reject the withdrawal request"""
        if self.status != 'pending':
            raise ValueError("Only pending withdrawals can be rejected")
        
        self.status = 'rejected'
        self.rejection_reason = reason
        self.approved_by = rejected_by
        self.approved_at = timezone.now()
        self.save()
    
    def calculate_net_amount(self):
        """Calculate net amount after processing fee"""
        self.net_amount = self.amount - self.processing_fee
        return self.net_amount