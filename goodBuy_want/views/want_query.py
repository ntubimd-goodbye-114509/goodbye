from django.shortcuts import render, redirect
from datetime import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import *

from ..models import *
from goodBuy_shop.models import Permission

from ..want_utils import *
from utils import *
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
    wants = wantInformation_many(Want.objects.filter(owner=user))
    # 看別人的只顯示公開
    if not request.user.is_authenticated or request.user != user:
        wants = wants.filter(permission__id=1)
        return render(request, '別人收物帖', locals())
    return render(request, '自己收物帖', locals())
# -------------------------
# 收物帖查詢 - want_id
# -------------------------
@want_exists_and_not_blacklisted()
@want_exists_required
def wantById_one(request, want):
    if request.user.is_authenticated and request.user.id == want.owner.id:
        backs = ( WantBack.objects.filter(want=want).select_related('user', 'shop').order_by('-date'))
        return render(request, '自己收物帖', locals())

    if want.permission.id == 2:
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

    want_ids_by_tag = WantTag.objects.filter(tag__name__icontains=kw).values_list('want_id', flat=True)

    wants = Want.objects.filter(
        Q(title__icontains=kw) | (Q(id__in=want_ids_by_tag) & Q(permission__id=1))
    ).distinct()

    # 排序方式處理
    if sort == 'new':
        wants = wants.order_by('-update')
    elif sort == 'old':
        wants = wants.order_by('update')
    else:
        messages.warning(request, "不支援的排序方式，已使用預設排序")
        wants = wants.order_by('-update')

    wants = wantInformation_many(wants)
    return render(request, '搜尋結果界面', locals())
# -------------------------
# 收物帖查詢 - tag_id
# -------------------------
@tag_exists_required
def wantByTag(request, tag):
    want_ids = WantTag.objects.filter(tag=tag).values_list('want_id', flat=True)

    wants = want.objects.filter(id__in=want_ids, permission__id=1)

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
