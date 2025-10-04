from platform import python_implementation
from django.db import models
from users.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.00)  # Changed from 19.00 to 0.00
    total_referral_earnings = models.FloatField(default=0.00)
    unwithdrawable_bonus = models.FloatField(default=0.00)  # Bonus that can be used to play
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.balance}"


class ChapaSession(models.Model):
    session_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=3)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    tx_ref = models.CharField(max_length=100)
    ref_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], max_length=10)
    def __str__(self):
        return f"{self.tx_ref} - {self.status}"


class AddisPaySession(models.Model):
    session_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=3)
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    tx_ref = models.CharField(max_length=100)
    ref_id = models.CharField(max_length=100)
    callback_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], max_length=10)
    def __str__(self):
        return f"{self.tx_ref} - {self.status}"



class ManualSession(models.Model):
    session_id = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    amount = models.FloatField()
    transaction_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], max_length=10)
    
    class Meta:
        verbose_name = "Manual Session"
        verbose_name_plural = "Manual Sessions"

    def __str__(self):
        return f"{self.session_id} - {self.status}"





class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    type = models.CharField(choices=[("DEPOSIT", "Deposit"), ("WITHDRAW", "Withdraw"),("BET", "Bet"),("WIN", "Win"),("REFERRAL_BONUS", "Referral Bonus")], max_length=20)
    status = models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], max_length=10)
    reference = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.type} - {self.status}"    



class WithdrawalRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    status = models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Withdrawal Request"
        verbose_name_plural = "Withdrawal Requests"

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"