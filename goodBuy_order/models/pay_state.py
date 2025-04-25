from django.db import models

# -------------------------
# 支付狀態
# -------------------------
class PayState(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name