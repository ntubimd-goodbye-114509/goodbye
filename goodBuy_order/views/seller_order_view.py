from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from goodBuy_shop.models import *
from goodBuy_web.models import *
from ..models import *
from ..utils import *
from goodBuy_shop.utils import shop_owner_required

# -------------------------
# 訂單顯示 - 賣家 - 全部 - 分類+all
# -------------------------
@login_required(login_url='login')
@shop_owner_required
def seller_order_list(request):
    state = request.GET.get('state')

    orders = Order.objects.filter(shop__owner=request.user)

    if state:
        if state == '7':
            orders = orders.filter(order_state_id__in=[7, 8, 9])
        else:
            orders = orders.filter(order_state_id=state)

    title = OrderState.objects.get(id=state).name if state else '全部' 

    return render(request, '賣家訂單顯示', locals())
# -------------------------
# 訂單顯示 - 賣家 - 單商店 - all
# -------------------------
@login_required(login_url='login')
@shop_owner_required
def seller_shop_order_list(request, shop):
    state = request.GET.get('state')

    orders = Order.objects.filter(shop=shop)

    if state:
        if state == '7':
            orders = orders.filter(order_state_id__in=[7, 8, 9])
        else:
            orders = orders.filter(order_state_id=state)

    title = OrderState.objects.get(id=state).name if state else '全部' 

    return render(request, '商店訂單界面', locals())
