from django.db import models
from .order import Order,ShopPayment

class OrderPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_account = models.ForeignKey(ShopPayment, on_delete=models.CASCADE)
    amount = models.IntegerField()  # 單次付款金額
    pay_time = models.DateTimeField(auto_now_add=True)
    pay_proof = models.ImageField(upload_to='pay_proofs/', blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)
    is_confirmed_by_seller = models.BooleanField(default=False)


    def __str__(self):
        if self.shop_payment and self.shop_payment.payment.id != 1:
            return f'於 {self.shop_payment.payment.name}（帳號：{self.shop_payment.account}）支付 {self.amount} 元 - {self.pay_time.strftime("%Y-%m-%d %H:%M")}'
        else:
            return f'選擇取貨付款 - 預計支付 {self.amount} 元 - {self.pay_time.strftime("%Y-%m-%d %H:%M")}'

