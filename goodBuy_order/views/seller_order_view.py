from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    title_map = {
        '1': '待買家選擇付款方式',
        '2': '賣家待確認',
        '3': '待付款',
        '4': '待出貨',
        '5': '已出貨',
        '6': '已收貨',
        '7': '未成立（缺貨）',
        '8': '未成立（訂單取消）',
        '9': '未成立（逾期未付款）',
    }

    orders = Order.objects.filter(shop__owner=request.user)

    if state:
        if state == '7':
            orders = orders.filter(order_state_id__in=[7, 8, 9])
        else:
            orders = orders.filter(order_state_id=state)

    title = title_map.get(state, '全部訂單')

    return render(request, '賣家訂單顯示', locals())
# -------------------------
# 訂單顯示 - 賣家 - 單商店 - all
# -------------------------

# -------------------------
# 訂單顯示 - 賣家 - 單商店 - 表格式統整
# -------------------------