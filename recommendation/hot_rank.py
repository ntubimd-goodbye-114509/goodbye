# recommendation/hot_rank.py
from collections import defaultdict
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from goodBuy_shop.models import ShopFootprints, Shop
from goodBuy_order.models.order import Order
from goodBuy_shop.models import Product


def get_hot_shops(limit=20, days=7):
    recent = timezone.now() - timedelta(days=days)
    scores = defaultdict(int)

    views = ShopFootprints.objects.filter(date__gte=recent).values('shop_id').annotate(vc=Count('id'))
    for v in views:
        scores[v['shop_id']] += v['vc']

    sales = Order.objects.filter(created_at__gte=recent).values_list('product__shop_id', flat=True)
    for sid in sales:
        scores[sid] += 2  # 銷售可加權

    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_ids = [sid for sid, _ in sorted_ids[:limit]]
    return Shop.objects.filter(id__in=top_ids)
