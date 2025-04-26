from django.db import models
# -------------------------
# 標籤
# -------------------------
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name