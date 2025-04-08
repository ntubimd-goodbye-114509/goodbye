from django.db.models import *
from django.contrib import messages
from django.shortcuts import *
from django.core.files.storage import FileSystemStorage
from datetime import timezone

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .utils import *
from .forms import *

def shopAll_update(request):
    shops = Shop.objects.filter(permission__id=1).order_by('-date')
    return render(request, '主頁', locals())

####################################################
# user_id查詢
@user_exists_required
def shopByUserId_many(request, user):
    shops = (
        Shop.objects
        .select_related('permission', 'shop_state', 'purchase_priority')
        .prefetch_related(
            Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
            Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
        ).filter(owner=user)
    )
    # 看別人的只顯示公開
    if not request.user.is_authenticated or request.user != user:
        shops = shops.filter(permission__id=1)
        return render(request, '別人主頁賣場', locals())
    return render(request, '自己主頁賣場', locals())

@shop_exists_required
def shopById_one(request, shop):
    shop = (
        shop.select_related('permission', 'shop_state', 'purchase_priority', 'owner')
        .prefetch_related(
            Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
            Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
        )
    )

    if request.user.is_authenticated and request.user.id == shop.owner.id:
        announcements = shop.shop_announcement_set.all().order_by('-date')
        return render(request, '自己賣場', locals())

    if shop.permission.id != 1:
        msg = '當前賣場不公開'
        return redirect('error')

    if request.user.is_authenticated:
        ShopFootprints.objects.update_or_create(
            user=request.user,
            shop=shop,
            defaults={'date': timezone.now()}
        )

    announcements = ShopAnnouncement.objects.filter(shop=shop).order_by('-date')
    return render(request, '別人賣場', locals())

def shopBySearch(request):
    kw = request.GET.get('keyWord')
    if not kw:
        messages.warning(request, "請輸入關鍵字")
        return redirect('home') 
    # tag相似搜索
    shop_ids_by_tag = ShopTag.objects.filter(tag__name__icontains=kw).values_list('shop_id', flat=True)
    # tag和name的
    shops = Shop.objects.filter(Q(name__icontains=kw) | (Q(id__in=shop_ids_by_tag) & Q(permission__id=1))).distinct()

    shops = shops.select_related('permission', 'shop_state', 'purchase_priority').prefetch_related(
        Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
        Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
    )
    return render(request, '搜尋結果界面', locals())

@tag_exists_required
def shopByTag(request, tag):
    shop_ids = ShopTag.objects.filter(tag=tag).values_list('shop_id', flat=True)

    shops = Shop.objects.filter(id__in=shop_ids, permission__id=1)

    shops = shops.select_related('permission', 'shop_state', 'purchase_priority').prefetch_related(
        Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
        Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
    )

    return render(request, '搜尋結果界面', locals())

@user_exists_required
def shopByPermissionId(request, user, permission_id):
    if not Permission.objects.filter(id=permission_id).exists():
        messages.error(request, "權限參數無效")
        return redirect('home')
    shops = (
        Shop.objects
        .select_related('permission', 'shop_state', 'purchase_priority')
        .prefetch_related(
            Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
            Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
        ).filter(owner=user, permission__id=permission_id).order_by('-date')
    )
    return render(request, '查詢完成頁面', locals())



