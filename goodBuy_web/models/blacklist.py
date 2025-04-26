from django.db import models
from .user import User
# -------------------------
# 黑名單
# -------------------------
class Blacklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fk_user_blacklist')
    black_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fk_black_blacklist')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'black_user'], name='unique_blacklist_pair')
        ]

    def __str__(self):
        return self.black_user  
