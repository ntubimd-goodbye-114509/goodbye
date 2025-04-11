from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import timezone

from ..models import *
from goodBuy_shop import Permission

from ..utils import *
from goodBuy_web.utils import *
from goodBuy_tag.utils import *

####################################################

def wantAll_update(request):
    wants = want.objects.filter(permission__id=1).order_by('-date')
    return render(request, '主頁', locals())

def wantInformation_many(wants):
    return (
        wants
        .select_related('permission')
        .prefetch_related(
            Prefetch('want_tag_set', queryset=WantTag.objects.select_related('tag')),
            Prefetch('images', queryset=WantImg.objects.filter(is_cover=True)),
        )
    )

####################################################

# user_id查詢
@user_exists_required
def wantByUserId_many(request, user):
    wants = wantInformation_many(want.objects.filter(owner=user))
    # 看別人的只顯示公開
    if not request.user.is_authenticated or request.user != user:
        wants = wants.filter(permission__id=1)
        return render(request, '別人收物帖', locals())
    return render(request, '自己收物帖', locals())

@want_exists_required
def wantById_one(request, want):
    if request.user.is_authenticated and request.user.id == want.owner.id:
        return render(request, '自己收物帖', locals())

    if want.permission.id != 1:
        messages.error(request, '當前收物帖不公開')
        return redirect('home')

    if request.user.is_authenticated:
        WantFootprints.objects.update_or_create(
            user=request.user,
            want=want,
            defaults={'date': timezone.now()}
        )
    return render(request, '別人收物帖', locals())

def wantBySearch(request):
    kw = request.GET.get('keyWord')
    if not kw:
        messages.warning(request, "請輸入關鍵字")
        return redirect('home') 
    # tag相似搜索
    want_ids_by_tag = WantTag.objects.filter(tag__name__icontains=kw).values_list('want_id', flat=True)
    # tag和name的
    wants = want.objects.filter(Q(name__icontains=kw) | (Q(id__in=want_ids_by_tag) & Q(permission__id=1))).distinct()

    wants = wantInformation_many(wants)
    return render(request, '搜尋結果界面', locals())

@tag_exists_required
def wantByTag(request, tag):
    want_ids = WantTag.objects.filter(tag=tag).values_list('want_id', flat=True)

    wants = want.objects.filter(id__in=want_ids, permission__id=1)

    wants = wantInformation_many(wants)

    return render(request, '搜尋結果界面', locals())

@user_exists_required
def wantByPermissionId(request, user, permission_id):
    if not Permission.objects.filter(id=permission_id).exists():
        messages.error(request, "權限參數無效")
        return redirect('home')
    wants = wantInformation_many(want.objects.filter(owner=user, permission__id=permission_id)).order_by('-date')

    return render(request, '查詢完成頁面', locals())
