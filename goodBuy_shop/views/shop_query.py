from django.db.models import *
from django.contrib import messages
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from datetime import timezone

from goodBuy_shop.models import *
from goodBuy_web.models import *
from goodBuy_order.models import IntentProduct

from recommendation.weighting import *
from recommendation.hot_rank import get_hot_shops

from utils import *
from ..shop_utils import *
from ..time_utils import *

# -------------------------
# 主頁商店推送（待加入演算法）
# -------------------------
def homepage(request):
    if request.user.is_authenticated:
        personalized = personalized_shop_recommendation(request.user, limit=10)
        hot = get_hot_shops(limit=10)
        hot = hot.exclude(id__in=[s.id for s in personalized])[:10]
        recommendations = list(personalized) + list(hot)
    else:
        recommendations = get_hot_shops(limit=20)
    
    return render(request, 'homepage.html', {'recommendations': recommendations})

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
@shop_exists_and_not_blacklisted()
def shopById_one(request, shop):
    is_rush_buy = shop.purchase_priority_id in [2, 3]

    products = list(Product.objects.filter(shop=shop))

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
        for product in products:
            product.is_out_of_stock = 1 if product.stock <= 0 else 0

    products.sort(key=lambda p: (p.is_out_of_stock, p.id))

    if request.user.is_authenticated and request.user.id == shop.owner.id:
        announcements = shop.shop_announcement_set.all().order_by('-date')
        return render(request, '自己賣場', locals())

    if shop.permission.id != 1:
        messages.error(request, '當前賣場不公開')
        return redirect('error')

    if request.user.is_authenticated:
        ShopFootprints.objects.update_or_create(
            user=request.user,
            shop=shop,
            defaults={'date': timezone.now()}
        )
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        ShopFootprints.objects.update_or_create(
            session_key=session_key,
            shop=shop,
            defaults={'date': timezone.now()}
        )

    announcements = ShopAnnouncement.objects.filter(shop=shop).order_by('-date')
    return render(request, '別人賣場', locals())
# -------------------------
# 商店查詢 - search
# -------------------------
from recommendation.weighting import personalized_shop_recommendation
from django.utils import timezone

def shopBySearch(request):
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
        shops = personalized_shop_recommendation(
            user=request.user,
            keywords=[kw],
            exclude_seen=False,  # 看過的商店依舊可出現
            limit=100
        )
    else:
        # 未登入使用者 fallback 為純搜尋關鍵字
        shop_ids_by_tag = ShopTag.objects.filter(tag__name__icontains=kw).values_list('shop_id', flat=True)
        shops = Shop.objects.filter(
            Q(name__icontains=kw) | Q(id__in=shop_ids_by_tag),
            permission__id=1
        ).distinct()

    # 排序
    if sort == 'old':
        shops = shops.order_by('update')
    else:
        shops = shops.order_by('-update')

    shops = shopInformation_many(shops)
    return render(request, '搜尋結果界面', locals())

# -------------------------
# 商店查詢 - tag
# -------------------------
@tag_exists_required
def shopByTag(request, tag):
    if request.user.is_authenticated:
        shops = personalized_shop_recommendation(
            user=request.user,
            tags=[tag.name],
            exclude_seen=False,
            limit=100
        )
    else:
        shop_ids = ShopTag.objects.filter(tag=tag).values_list('shop_id', flat=True)
        shops = Shop.objects.filter(id__in=shop_ids, permission__id=1)

    shops = shopInformation_many(shops)
    return render(request, '搜尋結果界面', locals())

# -------------------------
# 商店查詢 - 隱私狀況（ex.查詢自己私人的商店
# -------------------------
@login_required
def shopByPermissionId(request, permission_id):
    if permission_id not in [1, 2]:
        messages.error(request, "僅支援公開/私人可見的商店查詢")
        return redirect('home')

    shops = shopInformation_many(
        Shop.objects.filter(owner=request.user, permission__id=permission_id)
    ).order_by('-date')

    return render(request, '查詢完成頁面', locals())
