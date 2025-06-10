from collections import defaultdict
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from goodBuy_shop.models import Shop, Product, ShopFootprints, ShopCollect
from goodBuy_order.models.order import Order
from goodBuy_web.models.search_history import SearchHistory
from goodBuy_web.models.blacklist import BlackList
import random

# 活躍商店判斷
def get_active_shop_ids():
    now = timezone.now()
    recent_updated_ids = Shop.objects.filter(updated_at__gte=now - timedelta(days=60)).values_list('id', flat=True)
    recent_traded_pids = Order.objects.filter(created_at__gte=now - timedelta(days=7)).values_list('product_id', flat=True)
    recent_traded_shop_ids = Product.objects.filter(id__in=recent_traded_pids).values_list('shop_id', flat=True)
    return set(recent_updated_ids) | set(recent_traded_shop_ids), set(recent_traded_shop_ids)

# 商店資訊抓取關鍵資料
def extract_keywords_from_shops(shop_qs):
    keywords = set()
    for shop in shop_qs.only('tags', 'name', 'introduce'):
        if shop.tags:
            keywords.update(shop.tags.split(','))
        if shop.name:
            keywords.update(shop.name.split())
        if shop.introduce:
            keywords.update(shop.introduce.split())
    return keywords


# kw查詢排序
def score_shops_by_keywords(keywords, active_shop_ids, shop_queryset=None):
    scores = defaultdict(int)
    q = Q()
    for kw in keywords:
        q |= Q(tags__icontains=kw) | Q(name__icontains=kw) | Q(introduce__icontains=kw)

    matched_shops = Shop.objects.filter(q, id__in=active_shop_ids)
    if shop_queryset:
        matched_shops = matched_shops.filter(id__in=shop_queryset.values_list('id', flat=True))

    for shop in matched_shops:
        score = 0
        for kw in keywords:
            if kw in (shop.tags or ''):
                score += 5
            elif kw in (shop.name or ''):
                score += 3
            elif kw in (shop.introduce or ''):
                score += 2
        scores[shop.id] += score
    return scores

# 個性化評分部分商店
def compute_shop_scores(user, shop_queryset=None):
    now = timezone.now()
    scores = defaultdict(int)
    active_shop_ids, traded_shop_ids = get_active_shop_ids()
    shop_ids = set(shop_queryset.values_list('id', flat=True)) if shop_queryset else None

    def _add_score(sid, score):
        if (shop_ids is None or sid in shop_ids) and sid in active_shop_ids:
            scores[sid] += score

    # 搜尋關鍵字（最近一天）
    recent_keywords = list(
        SearchHistory.objects.filter(user=user, searched_at__gte=now - timedelta(days=1))
        .order_by('-searched_at').values_list('keyword', flat=True)[:3]
    )
    for kw in recent_keywords:
        for s in Shop.objects.filter(
            Q(name__icontains=kw) | Q(tags__icontains=kw),
            id__in=active_shop_ids
        ):
            _add_score(s.id, 5)

    cooldown = now - timedelta(days=14)
    fav_pids = ShopCollect.objects.filter(user=user, created_at__lt=cooldown).values_list('product_id', flat=True)
    bought_pids = Order.objects.filter(user=user).values_list('product_id', flat=True)
    related_pids = list(fav_pids) + list(bought_pids)
    related_shop_ids = Product.objects.filter(
        id__in=related_pids
    ).values_list('shop_id', flat=True).distinct()

    related_shops = Shop.objects.filter(id__in=related_shop_ids)

    keywords = extract_keywords_from_shops(related_shops)

    keyword_scores = score_shops_by_keywords(keywords, active_shop_ids, shop_queryset)
    for sid, score in keyword_scores.items():
        _add_score(sid, score)

    # 截取最近看過商店的tag等元素
    viewed_shop_ids = ShopFootprints.objects.filter(user=user, date__lt=cooldown).values_list('shop_id', flat=True)
    viewed_shops = Shop.objects.filter(id__in=viewed_shop_ids, id__in=active_shop_ids)
    for shop in viewed_shops:
        if shop.tags:
            for tag in shop.tags.split(','):
                for matched in Shop.objects.filter(tags__icontains=tag, id__in=active_shop_ids):
                    _add_score(matched.id, 4)

    # 活躍商店額外加分
    for sid in traded_shop_ids:
        _add_score(sid, 1)

    return scores


def personalized_homepage_shops_final(user, limit=20):
    now = timezone.now()
    active_shop_ids, _ = get_active_shop_ids()

    # 黑名單 + 自己排除
    blocked_ids = set(
        BlackList.objects.filter(blocker=user).values_list('blocked_id', flat=True)
    ) | set(
        BlackList.objects.filter(blocked=user).values_list('blocker_id', flat=True)
    )
    excluded_owner_ids = blocked_ids | {user.id}

    # 已看過商店
    seen_shop_ids = set(
        ShopFootprints.objects.filter(user=user).values_list('shop_id', flat=True)
    )

    # 打分 + 過濾
    scores = compute_shop_scores(user)
    new_ids = [sid for sid in scores if sid not in seen_shop_ids]
    level1_ids = [
        sid for sid in new_ids
        if Shop.objects.filter(id=sid, permission__id=1, id__in=active_shop_ids)
        .exclude(owner_id__in=excluded_owner_ids).exists()
    ]

    if len(level1_ids) >= limit:
        return Shop.objects.filter(id__in=level1_ids[:limit])

    # 熱門補齊
    from .hot_rank import get_hot_shops
    hot_ids = [
        s.id for s in get_hot_shops(limit=50)
        if s.id not in seen_shop_ids
        and s.owner_id not in excluded_owner_ids
        and s.id in active_shop_ids
    ]
    level2_needed = limit - len(level1_ids)
    level2_ids = hot_ids[:level2_needed]

    # 最近互動 fallback
    recent_bought_ids = Product.objects.filter(
        id__in=Order.objects.filter(user=user, created_at__gte=now - timedelta(days=14)).values_list('product_id', flat=True)
    ).values_list('shop_id', flat=True)

    recent_viewed_ids = ShopFootprints.objects.filter(
        user=user, date__gte=now - timedelta(days=7)
    ).values_list('shop_id', flat=True)

    recent_related_ids = list(set(recent_bought_ids) | set(recent_viewed_ids))
    recent_related_ids = [
        sid for sid in recent_related_ids
        if sid not in level1_ids + level2_ids
        and sid in active_shop_ids
        and Shop.objects.filter(id=sid, permission__id=1).exclude(owner_id__in=excluded_owner_ids).exists()
    ]
    fallback_needed = limit - len(level1_ids) - len(level2_ids)
    fallback_ids = recent_related_ids[:fallback_needed]

    # 組合推薦清單
    final_ids = level1_ids + level2_ids + fallback_ids
    random.shuffle(final_ids)
    return Shop.objects.filter(id__in=final_ids[:limit])
