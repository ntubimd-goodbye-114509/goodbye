# goodBuy_want/recommendation.py

from collections import defaultdict
from datetime import timedelta
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from goodBuy_want.models import Want, WantTag, WantFootprints, WantBack, WantRecommendationHistory
from goodBuy_web.models import SearchHistory
from goodBuy_want.recommend_config import (
    WANT_HOT_WEIGHTS, WANT_PERSONAL_WEIGHTS, WANT_KEYWORD_SCORES,
    RECOMMENDED_WANT_WEIGHT_MULTIPLIER,
    WANT_SEARCH_HISTORY_DAYS, WANT_VIEW_DAYS, WANT_REPLY_DAYS
)
from django.contrib.auth import get_user_model

User = get_user_model()

# -------------------------
# 擷取關鍵字
# -------------------------
def extract_keywords_from_wants(want_qs):
    keywords = set()
    for want in want_qs.only('title', 'post_text'):
        if want.title:
            keywords.update(want.title.split())
        if want.post_text:
            keywords.update(want.post_text.split())
        tags = WantTag.objects.filter(want=want).select_related('tag')
        for tag in tags:
            keywords.add(tag.tag.name)
    return keywords

# -------------------------
# 關鍵字評分
# -------------------------
def score_wants_by_keywords(keywords, want_queryset=None):
    scores = defaultdict(int)
    q = Q()
    for kw in keywords:
        q |= Q(title__icontains=kw) | Q(post_text__icontains=kw) | Q(wanttag__tag__name__icontains=kw)

    matched_wants = Want.objects.filter(q, permission__id=1).distinct()
    if want_queryset:
        matched_wants = matched_wants.filter(id__in=want_queryset.values_list('id', flat=True))

    for want in matched_wants:
        score = 0
        for kw in keywords:
            if kw in (want.title or ''):
                score += WANT_KEYWORD_SCORES.get('title', 0)
            elif kw in (want.post_text or ''):
                score += WANT_KEYWORD_SCORES.get('post_text', 0)
            elif WantTag.objects.filter(want=want, tag__name__icontains=kw).exists():
                score += WANT_KEYWORD_SCORES.get('tags', 0)
        scores[want.id] += score
    return scores

# -------------------------
# 個性化推薦分數
# -------------------------
def compute_want_scores(user, want_queryset=None):
    now = timezone.now()
    scores = defaultdict(int)
    want_ids = set(want_queryset.values_list('id', flat=True)) if want_queryset else None

    def _add_score(wid, score):
        if want_ids is None or wid in want_ids:
            scores[wid] += score

    # 搜尋紀錄
    keywords = list(
        SearchHistory.objects.filter(user=user, searched_at__gte=now - timedelta(days=WANT_SEARCH_HISTORY_DAYS))
        .order_by('-searched_at').values_list('keyword', flat=True)[:3]
    )
    kw_scores = score_wants_by_keywords(keywords, want_queryset)
    for wid, score in kw_scores.items():
        _add_score(wid, score + WANT_PERSONAL_WEIGHTS['search_keyword'])

    # 看過的 want
    viewed_ids = WantFootprints.objects.filter(user=user, date__gte=now - timedelta(days=WANT_VIEW_DAYS))
    viewed_wants = Want.objects.filter(id__in=viewed_ids.values_list('want_id', flat=True))
    viewed_keywords = extract_keywords_from_wants(viewed_wants)
    viewed_scores = score_wants_by_keywords(viewed_keywords, want_queryset)
    for wid, score in viewed_scores.items():
        _add_score(wid, score * WANT_PERSONAL_WEIGHTS['viewed_related_multiplier'])

    # 回覆過的 want
    replied_ids = WantBack.objects.filter(user=user, date__gte=now - timedelta(days=WANT_REPLY_DAYS))
    replied_wants = Want.objects.filter(id__in=replied_ids.values_list('want_id', flat=True))
    replied_keywords = extract_keywords_from_wants(replied_wants)
    reply_scores = score_wants_by_keywords(replied_keywords, want_queryset)
    for wid, score in reply_scores.items():
        _add_score(wid, score + WANT_PERSONAL_WEIGHTS['replied_related_bonus'])

    return scores

# -------------------------
# 個性化推薦主方法
# -------------------------
def personalized_want_recommendation(user, exclude_seen=True, limit=20, source='personalized', request=None):
    now = timezone.now()

    seen_ids = set()
    if exclude_seen:
        seen_ids = set(WantFootprints.objects.filter(user=user).values_list('want_id', flat=True))

    recent_ids = set(
        WantRecommendationHistory.objects.filter(user=user, recommended_at__gte=now - timedelta(days=7))
        .values_list('want_id', flat=True)
    )

    scores = compute_want_scores(user)
    for wid in list(scores):
        if wid in recent_ids:
            scores[wid] *= RECOMMENDED_WANT_WEIGHT_MULTIPLIER

    final_ids = [wid for wid in scores if wid not in seen_ids]
    if len(final_ids) > limit:
        final_ids = final_ids[:limit]

    # 寫入紀錄
    history_objs = []
    for wid in final_ids:
        obj_kwargs = {
            'want_id': wid,
            'source': source,
            'recommended_at': now,
        }
        if user.is_authenticated:
            obj_kwargs['user'] = user
        elif request:
            session_key = request.session.session_key or request.session.save()
            obj_kwargs['session_key'] = request.session.session_key
        history_objs.append(WantRecommendationHistory(**obj_kwargs))

    WantRecommendationHistory.objects.bulk_create(history_objs, ignore_conflicts=True)

    return Want.objects.filter(id__in=final_ids)
