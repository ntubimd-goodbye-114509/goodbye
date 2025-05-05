from django.db import models
from goodBuy_web.models import *
from goodBuy_shop.models import *
from .pay_state import *
from .order_state import *

# -------------------------
# 訂單
# -------------------------
class Order(models.Model):

    PAYMENT_MODE_CHOICES = [
        ('full', '一次付款'),
        ('split', '定金＋尾款'),
    ]
    PAYMENT_METHOD_CHOICES = [
    ('cash_on_delivery', '取貨付款'),
    ('remittance', '匯款'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    total = models.IntegerField()  # 總金額
    pay = models.IntegerField(blank=True, null=True)  # 已付款金額（自動計算）
    second_supplement = models.IntegerField(blank=True, null=True)  # 尚需補款

    date = models.DateTimeField(auto_now_add=True)
    payment_category = models.CharField(max_length=20,choices=PAYMENT_METHOD_CHOICES,default='cash_on_delivery')
    payment_mode = models.CharField(max_length=10,choices=PAYMENT_MODE_CHOICES,default='full')
    pay_state = models.ForeignKey(PayState, on_delete=models.CASCADE)
    order_state = models.ForeignKey(OrderState, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} 的訂單（{self.shop_name}） - {self.total} 元'

    # 已支付總金額
    @property
    def paid_total(self):
        return self.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0

    # 尚須付款金額
    @property
    def remaining_amount(self):
        return (self.total + (self.second_supplement or 0)) - self.paid_total
    
    # 是否已上傳付款憑證但尚未被確認或退回
    @property
    def has_pending_payment_proof(self):
        return self.payments.filter(is_paid_by_user=True, seller_state='wait_confirmed').exists()

