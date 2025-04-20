from django.db import models
from .order import Order

class OrderPayment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.IntegerField()  # 單次付款金額
    pay_time = models.DateTimeField(auto_now_add=True)
    pay_proof = models.ImageField(upload_to='pay_proofs/', blank=True, null=True)
    remark = models.CharField(max_length=255, blank=True, null=True)  # 例：定金、尾款、一次性付款

    def __str__(self):
        return f'{self.order} - 付款 {self.amount} 元（{self.remark or "未填寫"}）'
