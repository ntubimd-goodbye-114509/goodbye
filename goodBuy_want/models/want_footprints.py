from django.db import models
from goodBuy_web.models import User
from .want import Want
# -------------------------
# 收物帖足跡
# -------------------------
class WantFootprints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    want = models.ForeignKey(Want, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'want'], name='unique_user_want_footprints'),
            models.UniqueConstraint(fields=['session_key', 'want'], name='unique_session_want_footprints'),
        ]
    
    def __str__(self):
        identifier = self.user.username if self.user else f"匿名-{self.session_key}"
        return f"{identifier} - {self.want.name}"