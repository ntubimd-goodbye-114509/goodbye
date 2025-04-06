from django.db.models import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import *
from django.core.files.storage import FileSystemStorage
from datetime import datetime

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .shop_f import *
from .utils import *

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
        name = request.POST.get('name')
        introduce = request.POST.get('introduce')
        img = request.FILES.get('img')
        start_time = timeFormatChange_now(request.POST.get('start_time'))
        end_time = timeFormatChange_longtime(request.POST.get('end_time'))
        shop_state_id = request.POST.get('shop_state')
        permission_id = request.POST.get('permission')
        purchase_priority_id = request.POST.get('purchase_priority')
        # payment等前端出寫法再修改
        payment_account_ids = request.POST.getlist('payment_ids')
        # tag
        tag_ids = request.POST.getlist('tag_ids')

        shop = Shop.objects.create(name=name, owner=request.user,introduce=introduce,img=img,start_time=start_time,
                            end_time=end_time,shop_state=ShopState.objects.get(id=shop_state_id),
                            permission=Permission.objects.get(id=permission_id),purchase_priority=PurchasePriority.objects.get(id=purchase_priority_id))
        for payment_account_id in payment_account_ids:
            PaymentAccount.objects.create(shop=shop,payment=PaymentAccount.objects.get(id=payment_account_id))
        for tag_id in tag_ids:
            ShopTag.objects.create(shop=shop,tag=Tag.objects.get(id=tag_id))
        return render(request, '新增成功導向', locals())
    return render(request, '新增表單')

@shop_owner_required
def deleteShop(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    shop.delete()
    return redirect('刪除成功導向')

# 多樣同時修改
@shop_owner_required
def editShop(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    payments = ShopPayment.objects.select_related('Payment_Account').filter(shop=shop)
    tags = ShopTag.objects.select_related('Tag').filter(shop=shop)
    if request.method == 'POST':
        name = request.POST.get('name')
        introduce = request.POST.get('introduce')
        img = request.FILES.get('img')
        start_time = timeFormatChange_now(request.POST.get('start_time'))
        end_time = timeFormatChange_longtime(request.POST.get('end_time'))
        shop_state_id = request.POST.get('shop_state')
        permission_id = request.POST.get('permission')
        # payment等前端出寫法再寫
        payment_account_ids = request.POST.getlist('payment_ids')
        old_payment_account_ids = [p.payment_account.id for p in payments]
        tag_ids = payment_account_ids = request.POST.getlist('payment_ids')
        old_tag_ids = [t.tag_id for t in tags]

        shop.name = name
        shop.introduce = introduce
        shop.img = img
        shop.start_time = start_time
        shop.end_time = end_time
        shop.shop_state = ShopState.objects.get(id=shop_state_id)
        shop.permission = Permission.objects.get(id=permission_id)
        shop.save()

        # 有新出現的新增，沒出現的刪除
        # payment
        payment_to_add = set(payment_account_ids) - set(old_payment_account_ids)
        payment_to_remove = set(old_payment_account_ids) - set(payment_account_ids)
        for pid in payment_to_add:
            ShopPayment.objects.create(
                shop=shop,
                payment_account=PaymentAccount.objects.get(id=pid)
            )
        ShopPayment.objects.filter(shop=shop, payment_account__id__in=payment_to_remove).delete()
        # tag
        tag_to_add = set(tag_ids) - set(old_tag_ids)
        tag_to_remove = set(old_tag_ids) - set(tag_ids)
        for pid in tag_to_add:
            ShopTag.objects.create(
                shop=shop,
                tag=Tag.objects.get(id=pid)
            )
        ShopTag.objects.filter(shop=shop, tag__id__in=tag_to_remove).delete()
    return render(request, '修改成界面', locals())

####################################################
# 單項狀態修改
@shop_owner_required
def change_shop_state(request, shop_id, shop_state_id):
    shop = Shop.objects.get(id=shop_id)
    shop.shop_state = ShopState(id=shop_state_id)
    shop.save()
    return render(request, '')

@shop_owner_required
def change_permission(request, shop_id, permission_id):
    shop = Shop.objects.get(id=shop_id)
    shop.permission = Permission(id=permission_id)
    shop.save()
    return render(request, '')

@shop_owner_required
def change_start_time(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    start = timeFormatChange_now(request.GET.get('start_time'))
    shop.start_time = start
    shop.save()
    return render(request, '')

@shop_owner_required
def change_end_time(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    end = timeFormatChange_longtime(request.GET.get('end_time'))
    shop.start_time = end
    shop.save()
    return render(request, '')

####################################################
# 商店公告
@shop_exists_required
def showShopAnnouncement(request, shop_id):
    announcements = Shop_Announcement.objects.filter(shop=shop_id).order_by('-date')
    return render(request, '顯示公告頁面')

@shop_owner_required
def addAnnouncement(request, shop_id):
    if request.method == 'POST':
        shop = Shop.objects.get(id=shop_id)
        announcement = request.GET.get('announcement')
        Shop_Announcement.objects.create(shop=shop,announcement=announcement)
        return render(request, '新增完成界面')
    return render(request, '新增form')

@shop_owner_required
def deleteAnnouncement(request, shop_id, announcement_id):
    try:
        announcement = Shop_Announcement.objects.delete(id=announcement_id, shop__id=shop_id)
    except Shop_Announcement.DoesNotExist:
        return redirect('查無公告')
    return redirect('刪除成功導向')

@shop_owner_required
def editAnnouncement(request, shop_id, announcement_id):
    try:
        shop_announcement = Shop_Announcement.objects.get(id=announcement_id, shop_id=shop_id)
    except Shop_Announcement.DoesNotExist:
        return redirect('查無公告')
    if request.method == 'POST':
        announcement = request.POST.get('announcement')
        shop_announcement.announcement = announcement
        shop_announcement.date = datetime.strptime(datetime.now(), "%Y-%m-%dT%H:%M")
        shop_announcement.save()
        return render(request,' 修改完成界面')
    return render('修改form')

####################################################
