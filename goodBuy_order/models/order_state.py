from django.db import models

# -------------------------
# 訂單狀態
# -------------------------
class OrderState(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name