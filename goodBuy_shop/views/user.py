from django.db.models import *
from django.contrib import messages
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from datetime import timezone

from ..models import *
from goodBuy_web.models import *
from utils import *
from ..shop_utils import *

# -------------------------
# 收藏商店
# -------------------------
@login_required(login_url='login')
@shop_exists_required
def shop_collect_toggle(request, shop):
    if shop.owner == request.user:
        messages.warning(request, '不可以收藏自己的商店喔')
    else:
        obj = ShopCollect.objects.filter(user=request.user, shop=shop).first()
        if obj:
            obj.delete()
            messages.info(request, '已取消收藏')
        else:
            ShopCollect.objects.create(user=request.user, shop=shop, date=timezone.now())
            messages.success(request, '收藏成功')

    return redirect('商店界面', shop_id=shop.id)
# -------------------------
# 查看收藏的商店
# -------------------------
@login_required(login_url='login')
def my_shops_collected(request):
    shop_ids = ShopCollect.objects.filter(user=request.user).values_list('shop_id', flat=True)

    shops = shopInformation_many(Shop.objects.filter(id__in=shop_ids).order_by('-date'))
    return render(request, '收藏瀏覽頁面', locals())
# -------------------------
# 商店足跡
# -------------------------
@login_required(login_url='login')
def my_shop_footprints(request):
    shop_ids = ShopFootprints.objects.filter(user=request.user).values_list('shop_id', flat=True)
    shops = shopInformation_many(Shop.objects.filter(id__in=shop_ids).order_by('-date'))
    return render(request, '足跡頁面', locals())