from django.db import models

from django.db import models
from django.utils import timezone
from django.conf import settings

class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fk_user_search_history',
        null=True,       # 允許資料庫為 NULL
        blank=True       # 允許 admin/form 留白
    )
    keyword = models.CharField(max_length=100)
    searched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} searched '{self.keyword}' at {self.searched_at}"
