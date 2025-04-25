from django.db import models
from goodBuy_web.models import User
from .order import Order

# -------------------------
# 訂單評價&留言
# -------------------------
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    rank = models.IntegerField()
    comment = models.TextField()
    update = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'order'], name='unique_user_order_comment')
        ]
    
    def __str__(self):
        return f'{self.rank}{self.comment}'