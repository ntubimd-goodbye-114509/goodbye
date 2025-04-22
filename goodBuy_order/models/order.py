from django.db import models
from goodBuy_web.models import *
from goodBuy_shop.models import Shop
from .pay_state import *
from .order_state import *

class Order(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('full', '一次付款'),
        ('split', '定金＋尾款'),
    ]

    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    shop_name = models.CharField(max_length=255, blank=True, null=True)  # 備份商店名稱

    total = models.IntegerField()  # 總金額
    pay = models.IntegerField(blank=True, null=True)  # 已付款金額（自動計算）
    second_supplement = models.IntegerField(blank=True, null=True)  # 尚需補款

    date = models.DateTimeField(auto_now_add=True)

    payment_method = models.CharField(max_length=100)  # 使用者選擇的付款方式
    payment_mode = models.CharField(max_length=10,choices=PAYMENT_MODE_CHOICES,default='full')
    pay_state = models.ForeignKey(PayState, on_delete=models.CASCADE)
    order_state = models.ForeignKey(OrderState, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} 的訂單（{self.shop_name}） - {self.total} 元'

    @property
    def paid_total(self):
        return self.payments.aggregate(models.Sum('amount'))['amount__sum'] or 0

    @property
    def remaining_amount(self):
        return (self.total + (self.second_supplement or 0)) - self.paid_total
