from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from goodBuy_web.models import User
from goodBuy_want.models import Want

class WantRecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    want = models.ForeignKey(Want, on_delete=models.CASCADE)
    source = models.CharField(max_length=50)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    recommended_at = models.DateTimeField(default=timezone.now)
    clicked = models.BooleanField(default=False)
    algorithm_version = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'want']),
            models.Index(fields=['session_key', 'want']),
            models.Index(fields=['recommended_at']),
        ]

    def clean(self):
        if not self.user and not self.session_key:
            raise ValidationError("Either user or session_key must be set.")

    def __str__(self):
        identity = f"user {self.user_id}" if self.user else f"session {self.session_key}"
        return f"{identity} → want {self.want_id} ({self.source})"
