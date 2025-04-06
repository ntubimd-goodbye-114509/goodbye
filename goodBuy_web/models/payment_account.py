from django.db import models
from .user import User
from .payment import Payment
    
class PaymentAccount(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_accounts')
    img = models.ImageField(upload_to='payment_img/', blank=True, null=True)
    account = models.CharField(max_length=255, blank=True, null=True)