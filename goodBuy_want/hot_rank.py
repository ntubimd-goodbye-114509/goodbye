from collections import defaultdict
from datetime import timedelta
from django.db.models import Count, Q, When, Case, IntegerField
from django.utils import timezone

from goodBuy_want.models import Want, WantFootprints, WantBack, WantRecommendationHistory, WantTag
from goodBuy_want.recommend_config import HOT_WEIGHTS


def get_hot_wants(limit=None, days=7, keyword=None, tag=None, user=None, request=None, source='hot_rank'):
    now = timezone.now()
    recent = now - timedelta(days=days)
    scores = defaultdict(int)

    # 最近瀏覽數加分
    views = WantFootprints.objects.filter(date__gte=recent)
    if user:
        views = views.exclude(user=user)
    views = views.values('want_id').annotate(vc=Count('id'))
    for v in views:
        scores[v['want_id']] += v['vc'] * HOT_WEIGHTS['recent_views']

    # 最近被回覆加分
    replies = WantBack.objects.filter(date__gte=recent)
    if user:
        replies = replies.exclude(user=user)
    replies = replies.values('want_id').annotate(rc=Count('id'))
    for r in replies:
        scores[r['want_id']] += r['rc'] * HOT_WEIGHTS['recent_replies']

    # 排序與篩選
    sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_ids = [wid for wid, _ in sorted_ids]

    qs = Want.objects.filter(id__in=top_ids, permission__id=1)
    if keyword:
        qs = qs.filter(Q(title__icontains=keyword) | Q(post_text__icontains=keyword))

    if tag:
        tagged_ids = WantTag.objects.filter(tag=tag).values_list('want_id', flat=True)
        qs = qs.filter(id__in=tagged_ids)

    preserved_order = Case(
        *[When(id=wid, then=pos) for pos, wid in enumerate(top_ids)],
        output_field=IntegerField()
    )
    if limit:
        result_qs = qs.order_by(preserved_order)[:limit]
    else:
        result_qs = qs.order_by(preserved_order)

    # 無符合結果處理
    if not result_qs.exists():
        fallback_qs = Want.objects.filter(permission__id=1)
        if keyword:
            fallback_qs = fallback_qs.filter(Q(title__icontains=keyword) | Q(post_text__icontains=keyword))
        if tag:
            tagged_ids = WantTag.objects.filter(tag=tag).values_list('want_id', flat=True)
            fallback_qs = fallback_qs.filter(id__in=tagged_ids)

        result_qs = fallback_qs.order_by('-update')[:limit]

    # 寫入推薦紀錄
    recommended_at = timezone.now()
    history_objs = []
    for want in result_qs:
        obj_kwargs = {
            'want_id': want.id,
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

        history_objs.append(WantRecommendationHistory(**obj_kwargs))

    WantRecommendationHistory.objects.bulk_create(history_objs, ignore_conflicts=True)

    return result_qs
