from django.db.models import *
from django.contrib import messages
from django.shortcuts import *
from django.core.files.storage import FileSystemStorage
from datetime import timezone

from goodBuy_shop.models import *
from goodBuy_web.models import *
from goodBuy_order.models import IntentProduct

from ..utils import *
from ..shop_utils import *
from ..time_utils import *
from goodBuy_web.utils import *
from goodBuy_tag.utils import *

# -------------------------
# 主頁商店推送（待加入演算法）
# -------------------------
def shopAll_update(request):
    shops = Shop.objects.filter(permission__id=1).order_by('-date')
    return render(request, '主頁', locals())
# -------------------------
# 商店查詢 - user-id
# -------------------------
@user_exists_required
def shopByUserId_many(request, user):
    shops = shopInformation_many(Shop.objects.filter(owner=user))
    # 看別人的只顯示公開
    if not request.user.is_authenticated or request.user != user:
        shops = shops.filter(permission__id=1)
        return render(request, '別人主頁賣場', locals())
    return render(request, '自己主頁賣場', locals())
# -------------------------
# 商店查詢 - shop-id - 單一店鋪界面
# -------------------------
@shop_exists_required
def shopById_one(request, shop):
    is_rush_buy = shop.purchase_priority_id in [2, 3]

    products = list(Product.objects.filter(shop=shop))

    # 如果是搶購制且登入者存在，計算使用者剩餘可搶購量
    if is_rush_buy and request.user.is_authenticated:
        for product in products:
            user_claimed = IntentProduct.objects.filter(
                product=product,
                intent__user=request.user,
                intent__shop=shop
            ).aggregate(total=Sum('quantity'))['total'] or 0

            remaining_quantity = max(product.stock - user_claimed, 0)
            product.remaining_quantity = remaining_quantity
            product.claimed_quantity = user_claimed
            product.is_out_of_stock = 1 if remaining_quantity <= 0 else 0

    else:
        # 一般模式，直接看是否缺貨
        for product in products:
            product.is_out_of_stock = 1 if product.stock <= 0 else 0

    # 根據 is_out_of_stock + id 排序：缺貨移後面
    products.sort(key=lambda p: (p.is_out_of_stock, p.id))

    # 自己的賣場
    if request.user.is_authenticated and request.user.id == shop.owner.id:
        announcements = shop.shop_announcement_set.all().order_by('-date')
        return render(request, '自己賣場', locals())

    # 別人的賣場但不公開
    if shop.permission.id != 1:
        messages.error(request, '當前賣場不公開')
        return redirect('error')

    # 留下足跡
    if request.user.is_authenticated:
        ShopFootprints.objects.update_or_create(
            user=request.user,
            shop=shop,
            defaults={'date': timezone.now()}
        )

    announcements = ShopAnnouncement.objects.filter(shop=shop).order_by('-date')
    return render(request, '別人賣場', locals())
# -------------------------
# 商店查詢 - search
# -------------------------
def shopBySearch(request):
    kw = request.GET.get('keyWord')
    if not kw:
        messages.warning(request, "請輸入關鍵字")
        return redirect('home') 
    # tag相似搜索
    shop_ids_by_tag = ShopTag.objects.filter(tag__name__icontains=kw).values_list('shop_id', flat=True)
    # tag和name的
    shops = Shop.objects.filter(Q(name__icontains=kw) | (Q(id__in=shop_ids_by_tag) & Q(permission__id=1))).distinct()

    shops = shopInformation_many(shops)
    return render(request, '搜尋結果界面', locals())
# -------------------------
# 商店查詢 - tag
# -------------------------
@tag_exists_required
def shopByTag(request, tag):
    shop_ids = ShopTag.objects.filter(tag=tag).values_list('shop_id', flat=True)

    shops = Shop.objects.filter(id__in=shop_ids, permission__id=1)

    shops = shopInformation_many(shops)

    return render(request, '搜尋結果界面', locals())
# -------------------------
# 商店查詢 - 隱私狀況（ex.查詢自己私人的商店
# -------------------------
@user_exists_required
def shopByPermissionId(request, user, permission_id):
    if not Permission.objects.filter(id=permission_id).exists():
        messages.error(request, "權限參數無效")
        return redirect('home')
    shops = shopInformation_many(Shop.objects.filter(owner=user, permission__id=permission_id)).order_by('-date')

    return render(request, '查詢完成頁面', locals())
