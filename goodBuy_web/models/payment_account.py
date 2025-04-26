from django.db import models
from .user import User
from .payment import Payment
# -------------------------
# 支付方式帳號存在檢查
# -------------------------
class ActivePaymentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)
# -------------------------
# 使用者各支付方式帳號
# -------------------------
class PaymentAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_accounts')
    img = models.ImageField(upload_to='payment_img/', blank=True, null=True)
    account = models.CharField(max_length=255)
    is_delete = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'payment', 'account'],
                name='unique_payment_account'
            )
        ]

    objects = models.Manager()
    active = ActivePaymentManager()

    def __str__(self):
        return self.payment.name