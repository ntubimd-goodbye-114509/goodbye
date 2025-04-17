from django.db import models
from .user import User
from .payment import Payment
    
class PaymentAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_accounts')
    img = models.ImageField(upload_to='payment_img/', blank=True, null=True)
    account = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'payment'], name='unique_user_payment_account')
        ]
    
    def __str__(self):
        return f'{self.payment.name}: {self.account}'