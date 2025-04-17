from django.db import models
from goodBuy_web.models import User
from .want import Want

class WantFootprints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    want = models.ForeignKey(Want, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'want'], name='unique_user_want_footprints')
        ]
    
    def __str__(self):
        return self.want