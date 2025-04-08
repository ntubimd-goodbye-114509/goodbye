from django.db.models import *
from django.contrib import messages
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from datetime import timezone

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .utils import *

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

@login_required(login_url='login')
def my_collected_shops(request):
    shop_ids = ShopCollect.objects.filter(user=request.user).values_list('shop_id', flat=True)

    shops = (
        Shop.objects
        .filter(id__in=shop_ids)
        .select_related('permission', 'shop_state', 'purchase_priority')
        .prefetch_related(
            Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
            Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
        )
        .order_by('-date')
    )

    return render(request, '收藏瀏覽頁面', locals())