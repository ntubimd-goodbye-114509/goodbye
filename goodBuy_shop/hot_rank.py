from collections import defaultdict
from datetime import timedelta
from django.db.models import Count, Q, When, Case, IntegerField
from django.utils import timezone

from goodBuy_shop.models import Shop, ShopFootprints, ShopTag, ShopRecommendationHistory
from goodBuy_order.models import ProductOrder
from goodBuy_shop.recommend_config import HOT_WEIGHTS
from goodBuy_shop.shop_utils import shop_is_active


def get_hot_shops(limit=20, days=7, owner=None, keyword=None, tag=None, user=None, request=None, source='hot_rank'):
    now = timezone.now()
    recent = now - timedelta(days=days)
    scores = defaultdict(int)

    # 最近瀏覽
    views = ShopFootprints.objects.filter(date__gte=recent)
    if owner:
        views = views.filter(shop__owner=owner)
    views = views.values('shop_id').annotate(vc=Count('id'))
    for v in views:
        scores[v['shop_id']] += v['vc'] * HOT_WEIGHTS['recent_views']

    # 最近成交
    sales = ProductOrder.objects.filter(
        order__date__gte=recent,
        order__order_state__id__in=[4, 5, 6]
    )
    if owner:
        sales = sales.filter(product__shop__owner=owner)
    sales = sales.values_list('product__shop_id', flat=True)
    for sid in sales:
        scores[sid] += HOT_WEIGHTS['recent_sales']

    # 新開店加分
    new_shop_ids = Shop.objects.filter(
        start_time__gte=now - timedelta(days=3)
    ).values_list('id', flat=True)
    for sid in new_shop_ids:
        scores[sid] += HOT_WEIGHTS['new_shop_bonus']

    # 排序
    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_ids = [sid for sid, _ in sorted_ids]

    # 基本條件（公開 + 未過期）
    qs = Shop.objects.filter(id__in=top_ids, permission__id=1).filter(shop_is_active(now))
    if owner:
        qs = qs.filter(owner=owner)

    if keyword:
        qs = qs.filter(
            Q(name__icontains=keyword) |
            Q(tags__icontains=keyword) |
            Q(introduce__icontains=keyword)
        )

    if tag:
        tagged_ids = ShopTag.objects.filter(tag=tag).values_list('shop_id', flat=True)
        qs = qs.filter(id__in=tagged_ids)

    # 排序還原
    preserved_order = Case(
        *[When(id=sid, then=pos) for pos, sid in enumerate(top_ids)],
        output_field=IntegerField()
    )
    result_qs = qs.order_by(preserved_order)[:limit]

    # 無符合結果處理
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

    # 寫入推薦紀錄
    recommended_at = timezone.now()
    history_objs = []

    for shop in result_qs:
        obj_kwargs = {
            'shop_id': shop.id,
            'source': source,
            'recommended_at': recommended_at,
        }
        if user and user.is_authenticated:
            obj_kwargs['user'] = user
        elif request:
            session_key = request.session.session_key or request.session.save()
            obj_kwargs['session_key'] = request.session.session_key
        else:
            continue  # 無身分資訊不記錄

        history_objs.append(ShopRecommendationHistory(**obj_kwargs))

    ShopRecommendationHistory.objects.bulk_create(history_objs, ignore_conflicts=True)

    return result_qs
