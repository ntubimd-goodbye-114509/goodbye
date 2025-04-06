from django.db import models

class PayState(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)