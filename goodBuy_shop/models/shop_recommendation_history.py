from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from goodBuy_shop.models import Shop
from goodBuy_web.models import User


class ShopRecommendationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    source = models.CharField(max_length=50)
    keyword = models.CharField(max_length=255, blank=True, null=True)
    recommended_at = models.DateTimeField(default=timezone.now)
    clicked = models.BooleanField(default=False)
    algorithm_version = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'shop']),
            models.Index(fields=['session_key', 'shop']),
            models.Index(fields=['recommended_at']),
        ]

    def clean(self):
        if not self.user and not self.session_key:
            raise ValidationError("Either user or session_key must be set.")

    def __str__(self):
        identity = f"user {self.user_id}" if self.user else f"session {self.session_key}"
        return f"{identity} → shop {self.shop_id} ({self.source})"
