from django.db.models.signals import post_save
from django.dispatch import receiver
from goodBuy_web.models import *

#在 User 創建時自動建立 Profile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print("signals.py tr")  

    if created:
        Profile.objects.create(user=instance)
        print('Profile auto-created')