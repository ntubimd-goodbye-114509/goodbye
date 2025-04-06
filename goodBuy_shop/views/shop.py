from django.db.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import *
from django.core.files.storage import FileSystemStorage
from datetime import datetime

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .utils import *
from .forms import *
from .shop_f import *

def shopAll_update(request):
    shops = Shop.objects.filter(permission__id=1).order_by('-date')
    return render(request, '主頁', locals())

####################################################
# user_id查詢
@user_exists_required
def shopByUserId_many(request, user_id):
    shops = (
        Shop.objects
        .select_related('permission', 'shop_state', 'purchase_priority')
        .prefetch_related(
            Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
            Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
        ).get(owner__id=user_id)
    )
    # 看別人的只顯示公開
    if not request.user.is_authenticated or request.user.id != user_id:
        shops = shops.filter(permission__id=1)
        return render(request, '別人主頁賣場', locals())
    return render(request, '自己主頁賣場', locals())

@shop_exists_required
def shopById_one(request, shop_id):
    shop = (
        Shop.objects
        .select_related('permission', 'shop_state', 'purchase_priority')  # 抓 FK
        .prefetch_related(
            Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
            Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
        ).get(id=shop_id)  # 你想查的商店
    )
    announcements = Shop_Announcement.objects.filter(shop=shop_id).order_by('-date')
    # 別人的
    if not request.user.is_authenticated or request.user.id != shop.owner.id:
        if shop.permission.id != 1:
            shop = None
            announcements = None
            msg = '當前賣場不公開'
        return render(request, '別人賣場', locals())
    return render(request, '自己賣場', locals())

def shopBySearch(request):
    kw = request.GET.get('keyWord')
    # tag相似搜索
    shop_ids_by_tag = ShopTag.objects.filter(tag__name__icontains=kw).values_list('shop_id', flat=True)
    # tag和name的
    shops = Shop.objects.filter(Q(name__icontains=kw) | Q(id__in=shop_ids_by_tag) & Q(permission__id=1)).distinct()

    shops = shops.select_related('permission', 'shop_state', 'purchase_priority').prefetch_related(
        Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
        Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
    )
    return render(request, '搜尋結果界面', locals())

@tag_exists_required
def shopByTag(request, tag_id):
    shop_ids = ShopTag.objects.filter(tag_id=tag_id).values_list('shop_id', flat=True)

    shops = Shop.objects.filter(id__in=shop_ids, permission__id=1)

    shops = shops.select_related('permission', 'shop_state', 'purchase_priority').prefetch_related(
        Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
        Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
    )

    return render(request, '搜尋結果界面', locals())

@user_exists_required
def shopByPermissionId(request, user_id, permission_id):
    shops = (
        Shop.objects
        .select_related('permission', 'shop_state', 'purchase_priority')
        .prefetch_related(
            Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
            Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
        ).get(owner__id=user_id, permission__id=permission_id)
    )
    return render(request, '查詢完成頁面', locals())

####################################################
# 商店
@login_required(login_url='login')
def addShop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '新增成功')
            return redirect('shop_list')
        else:
            messages.error(request, '新增失敗')
    else:
        form = ShopForm(user=request.user)
    return render(request, 'shop_form.html', {'form': form})

@shop_owner_required
def deleteShop(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    shop.delete()
    messages.success(request, '刪除成功！')
    return redirect('刪除成功導向')

# 多樣同時修改
@shop_owner_required
def edit_shop(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '修改成功')
            return redirect('shop_detail', shop_id=shop.id)
        else:
            messages.error(request, '修改失敗')
    else:
        form = ShopForm(instance=shop, user=request.user)

    return render(request, '商店修改', locals())

####################################################
# 單項狀態修改
@shop_owner_required
def change_shop_state(request, shop_id, shop_state_id):
    shop = Shop.objects.get(id=shop_id)
    shop.shop_state = ShopState(id=shop_state_id)
    shop.save()
    messages.success(request, '修改成功')
    return render(request, '')

@shop_owner_required
def change_permission(request, shop_id, permission_id):
    shop = Shop.objects.get(id=shop_id)
    shop.permission = Permission(id=permission_id)
    shop.save()
    messages.success(request, '修改成功')
    return render(request, '')

@shop_owner_required
def change_start_time(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    start = timeFormatChange_now(request.GET.get('start_time'))
    shop.start_time = start
    shop.save()
    messages.success(request, '修改成功')
    return render(request, '')

@shop_owner_required
def change_end_time(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    end = timeFormatChange_longtime(request.GET.get('end_time'))
    shop.start_time = end
    shop.save()
    messages.success(request, '修改成功')
    return render(request, '')

####################################################
# 商店公告
@shop_exists_required
def showShopAnnouncement(request, shop_id):
    announcements = Shop_Announcement.objects.filter(shop=shop_id).order_by('-date')
    return render(request, '顯示公告頁面')

@shop_owner_required
def addAnnouncement(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.shop = shop  # 綁定店家
            announcement.save()
            messages.success(request, '公告新增成功')
            return redirect('shop_detail', shop_id=shop.id)
        else:
            messages.error(request, '公告新增失敗')
    else:
        form = AnnouncementForm()

    return render(request, 'announcement_form.html', locals())

@shop_owner_required
def deleteAnnouncement(request, shop_id, announcement_id):
    try:
        announcement = Shop_Announcement.objects.delete(id=announcement_id, shop__id=shop_id)
    except Shop_Announcement.DoesNotExist:
        messages.error(request, '查無公告')
        return redirect('查無公告')
    messages.success(request, '刪除成功')
    return redirect('刪除成功導向')

@shop_owner_required
def editAnnouncement(request, shop_id, announcement_id):
    shop = get_object_or_404(Shop, id=shop_id)
    announcement = get_object_or_404(Shop_Announcement, id=announcement_id, shop=shop)
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, '公告修改成功')
            return redirect('shop_detail', shop_id=shop.id)
        else:
            messages.error(request, '公告修改失敗')
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, 'announcement_form.html', locals())

####################################################
