from django.db import models
from users.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.00)
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
    trx_ref = models.CharField(max_length=100)
    ref_id = models.CharField(max_length=100)
    callback_url = models.URLField()
    return_url = models.URLField()
    customization = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], max_length=10)
    def __str__(self):
        return f"{self.trx_ref} - {self.status}"





class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    type = models.CharField(choices=[("DEPOSIT", "Deposit"), ("WITHDRAW", "Withdraw")], max_length=20)
    status = models.CharField(choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], max_length=10)
    reference = models.CharField(max_length=100,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.type} - {self.status}"    