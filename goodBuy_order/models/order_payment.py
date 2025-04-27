from django.utils import timezone
from django.db import models
from .order import Order,ShopPayment

# -------------------------
# 訂單支付資料
# -------------------------
class OrderPayment(models.Model):
    SELLER_CHOICES = [
        ('wait confirmed','待確認'),
        ('confirmed','已收到'),
        ('returned','已退回'),
        ('none', '取貨付款')
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    shop_payment = models.ForeignKey(ShopPayment, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.IntegerField()
    pay_time = models.DateTimeField(auto_now_add=True)
    pay_proof = models.ImageField(upload_to='pay_proofs/', blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)

    is_paid_by_user = models.BooleanField(default=False)

    seller_state = models.CharField(max_length=20,choices=SELLER_CHOICES,default='wait confirmed')

    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        method = self.shop_payment.payment.name if self.shop_payment and self.shop_payment.payment else "未知方式"
        account = self.shop_payment.account if self.shop_payment else "無帳號"

        # 狀態判斷
        if self.deadline and timezone.now() > self.deadline:
            status = '已逾期'
        elif self.seller_state == 'returned':
            status = '已退回'
        elif self.seller_state == 'confirmed':
            status = '已確認收款'
        elif self.is_paid_by_user:
            status = '使用者已上傳憑證'
        else:
            status = '待使用者付款'

        return f'{method}（{account}）支付 {self.amount} 元｜{status}'
