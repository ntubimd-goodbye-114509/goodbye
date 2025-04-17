from django.db import models
from goodBuy_tag.models import Tag
from .want import Want

class WantTag(models.Model):
    want = models.ForeignKey(Want, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['want', 'tag'], name='unique_want_tag')
        ]
    
    def __str__(self):
        return self.tag