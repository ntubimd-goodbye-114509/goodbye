# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Shop
from .utils import allocate_rush_orders

@shared_task
def process_rush_shop_orders(shop_id):
    from .models import Shop
    shop = Shop.objects.get(id=shop_id)
    if shop.end_time <= timezone.now() and shop.purchase_priority_id in [2, 3]:
        allocate_rush_orders(shop)
