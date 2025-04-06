from django.db import models
from .user import User

class Blacklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fk_user_blacklist')
    black_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fk_black_blacklist')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.black_user  