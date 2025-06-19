from collections import defaultdict
from datetime import timedelta
from django.db.models import Count, Q, When, Case, IntegerField
from django.utils import timezone

from goodBuy_shop.models import Shop, ShopFootprints, ShopTag
from goodBuy_order.models import ProductOrder

from .utils import *
# -------------------------
# 熱門商店推薦
# -------------------------
def get_hot_shops(limit=20, days=7, owner=None, keyword=None, tag=None):
    now = timezone.now()
    recent = now - timedelta(days=days)
    scores = defaultdict(int)   

    # 最近瀏覽數
    views = ShopFootprints.objects.filter(date__gte=recent).values('shop_id').annotate(vc=Count('id'))
    if owner:
        views = views.filter(shop__owner=owner)
    for v in views:
        scores[v['shop_id']] += v['vc']

    # 最近已完成訂單
    sales = ProductOrder.objects.filter(
        order__date__gte=recent,
        order__order_state__id__in=[4, 5, 6]
    ).values_list('product__shop_id', flat=True)
    if owner:
        sales = sales.filter(product__shop__owner=owner)
    for sid in sales:
        scores[sid] += 2

    # 發佈3天內額外加分
    new_shop_ids = Shop.objects.filter(
        start_time__gte=now - timedelta(days=3)
    ).values_list('id', flat=True)
    for sid in new_shop_ids:
        scores[sid] += 3 

    # 排序
    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_ids = [sid for sid, _ in sorted_ids]

    # 基本條件（公開 + 未截止）
    qs = Shop.objects.filter(id__in=top_ids, permission__id=1).filter(shop_is_active(now))
    if owner:
        qs = qs.filter(owner=owner)

    # 關鍵字篩選
    if keyword:
        qs = qs.filter(
            Q(name__icontains=keyword) |
            Q(tags__icontains=keyword) |
            Q(introduce__icontains=keyword)
        )

    # tag 篩選
    if tag:
        tagged_ids = ShopTag.objects.filter(tag=tag).values_list('shop_id', flat=True)
        qs = qs.filter(id__in=tagged_ids)

    # 排序還原（按照 score 順序）
    preserved_order = Case(
        *[When(id=sid, then=pos) for pos, sid in enumerate(top_ids)],
        output_field=IntegerField()
    )

    result_qs = qs.order_by(preserved_order)[:limit]

    # fallback ➜ 如果結果為空，使用 update 排序
    if not result_qs.exists():
        fallback_qs = Shop.objects.filter(
            permission__id=1
        ).filter(shop_is_active(now))

        if keyword:
            fallback_qs = fallback_qs.filter(
                Q(name__icontains=keyword) |
                Q(tags__icontains=keyword) |
                Q(introduce__icontains=keyword)
            )

        if tag:
            tagged_ids = ShopTag.objects.filter(tag=tag).values_list('shop_id', flat=True)
            fallback_qs = fallback_qs.filter(id__in=tagged_ids)

        result_qs = fallback_qs.order_by('-update')[:limit]

    return result_qs