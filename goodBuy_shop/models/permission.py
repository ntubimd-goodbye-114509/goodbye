from django.db import models

# -------------------------
# 隱私狀態（公開、私人、已刪除）
# want可用
# -------------------------
class Permission(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name  