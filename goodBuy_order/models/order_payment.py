from datetime import timezone
from django.db import models
from .order import Order,ShopPayment

class OrderPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    shop_payment = models.ForeignKey(ShopPayment, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    pay_time = models.DateTimeField(auto_now_add=True)
    pay_proof = models.ImageField(upload_to='pay_proofs/', blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    # 使用者標記已付款（通常為上傳匯款憑證）
    is_paid_by_user = models.BooleanField(default=False)

    # 賣家確認是否收到匯款
    is_confirmed_by_seller = models.BooleanField(default=False)

    # 賣家主動退回匯款（例如金額錯誤、逾期未確認）
    is_rejected_by_seller = models.BooleanField(default=False)

    # 賣家給予匯款期限（可選）
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        method = self.shop_payment.payment.name if self.shop_payment and self.shop_payment.payment else "未知方式"
        account = self.shop_payment.account if self.shop_payment else "無帳號"
        status = '待確認'
        if self.is_confirmed_by_seller:
            status = '已確認'
        elif self.is_rejected_by_seller:
            status = '已退回'
        elif self.deadline and timezone.now() > self.deadline:
            status = '已逾期'

        return f'{method}（{account}）支付 {self.amount} 元｜{status}'
