from django.shortcuts import render, redirect
from datetime import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import *

from ..models import *
from goodBuy_shop.models import Permission
from goodBuy_web.models import SearchHistory

from ..want_utils import *
from utils import *

from weighting import *
from hot_rank import *
# -------------------------
# 收物帖主頁推送
# -------------------------
def wantAll_update(request):
    wants = want.objects.filter(permission__id=1).order_by('-date')
    return render(request, '主頁', locals())

# -------------------------
# 收物帖查詢 - user_id
# -------------------------
@user_exists_required
def wantByUserId_many(request, user):
    wants = Want.objects.filter(owner=user)
    if not request.user.is_authenticated or request.user != user:
        wants = wants.filter(permission__id=1)

        if request.user.is_authenticated:
            recommended = personalized_want_recommendation(request.user, want_queryset=wants)
        else:
            recommended = get_hot_wants(limit=20)
            recommended = [w for w in recommended if w.user_id == user.id]

        wants = wantInformation_many(recommended)
        return render(request, '別人收物帖', locals())
    
    wants = wantInformation_many(wants)
    return render(request, 'want_detail.html', locals())

# -------------------------
# 收物帖查詢 - want_id
# -------------------------
@want_exists_and_not_blacklisted()
def wantById_one(request, want):
    if request.user.is_authenticated and request.user == want.user:
        backs = ( WantBack.objects.filter(want=want).select_related('user', 'shop').order_by('-date'))
        return render(request, 'want_detail.html', locals())

    if want.permission.id == 2 and request.user != want.owner:
        messages.error(request, '當前收物帖不公開')
        return redirect('home')
    if want.permission.id == 3:
        messages.error(request, '當前收物帖不存在')
        return redirect('home')

    if request.user.is_authenticated:
        WantFootprints.objects.update_or_create(
            user=request.user,
            want=want,
            defaults={'date': timezone.now()}
        )
    else:
        # 確保 session_key 存在
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        WantFootprints.objects.update_or_create(
            session_key=session_key,
            want=want,
            defaults={'date': timezone.now()}
        )
    
    return render(request, '別人收物帖', locals())

# -------------------------
# 收物帖查詢 - search
# -------------------------
def wantBySearch(request):
    kw = request.GET.get('keyWord')
    sort = request.GET.get('sort', 'new')

    if not kw:
        messages.warning(request, "請輸入關鍵字")
        return redirect('home')

    if request.user.is_authenticated:
        SearchHistory.objects.update_or_create(
            user=request.user,
            keyword=kw,
            searched_at=timezone.now()
        )

    if request.user.is_authenticated:
        wants = personalized_want_recommendation(
            user=request.user,
            keywords=[kw],
            exclude_seen=False,
            limit=100
        )
    else:
        wants = get_hot_wants(limit=100, keyword=kw)

    # 排序
    if sort == 'old':
        wants = wants.order_by('update')
    else:
        wants = wants.order_by('-update')

    wants = wantInformation_many(wants)
    return render(request, '搜尋結果界面', locals())

# -------------------------
# 收物帖查詢 - tag_id
# -------------------------
@tag_exists_required
def wantByTag(request, tag):
    if request.user.is_authenticated:
        wants = personalized_want_recommendation(
            user=request.user,
            tags=[tag.name],
            exclude_seen=False,
            limit=100
        )
    else:
        wants = get_hot_wants(limit=100, tag=tag)

    wants = wantInformation_many(wants)
    return render(request, '搜尋結果界面', locals())

# -------------------------
# 收物帖查詢 - permission_id
# -------------------------
@login_required(login_url='login')
def wantByPermissionId(request, permission_id):
    if permission_id not in [1, 2]:
        messages.error(request, "僅支援公開/私人可見的收物帖查詢")
        return redirect('home')
    wants = wantInformation_many(Want.objects.filter(owner=request.user, permission__id=permission_id)).order_by('-date')

    return render(request, '查詢完成頁面', locals())
