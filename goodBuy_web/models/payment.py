from django.db import models
# -------------------------
# 支付方式
# -------------------------
class Payment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name 