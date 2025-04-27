from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict
from django.utils import timezone

from goodBuy_shop.models import *
from goodBuy_shop.utils import shop_exists_required
from goodBuy_web.models import *
from ..models import *
from ..utils import *
# -------------------------
# 訂單顯示 - 使用者 - 全部 - 分類+all
# -------------------------
@login_required(login_url='login')
def buyer_order_list(request):
    state = request.GET.get('state')

    orders = Order.objects.filter(user=request.user)

    if state:
        if state == '7':
            orders = orders.filter(order_state_id__in=[7, 8, 9])
        else:
            orders = orders.filter(order_state_id=state)

    title = OrderState.objects.get(id=state).name if state else '全部' 

    return render(request, '買家訂單顯示', locals())
# -------------------------
# 待付款&付款記錄顯示 - 使用者
# -------------------------
