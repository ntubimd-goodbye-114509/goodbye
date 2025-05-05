from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from goodBuy_order.models import Order
from goodBuy_shop.models import ShopPayment
from django.shortcuts import redirect, render

from ..forms import OrderPaymentForm
from utils import order_buyer_required, order_seller_required
# -------------------------
# 訂單狀態修改 - ex. 付款、出貨
# -------------------------
# 買家訂單狀態修改
# -------------------------
@order_buyer_required(redirect_to='buyer_order_list')
def buyer_order_confirm(request, order):
    if order.order_state_id == 5:
        order.order_state_id = 6
        messages.success(request, '已確認收貨')
    else:
        messages.error(request, '操作無效或狀態錯誤')
        return redirect(request.META.get('HTTP_REFERER') or 'home')
    
    order.save()
    return redirect('訂單已完成清單頁面')
# -------------------------
# 賣家訂單狀態修改
# -------------------------
@order_seller_required(redirect_to='seller_order_list')
def seller_action(request, order):
    action = request.POST.get('action')

    if order.order_state_id == 2 and action == 'confirm_order':
        order.order_state_id = 3
        messages.success(request, '訂單已確認')
    elif order.order_state_id == 2 and action == 'reject_stock':
        order.order_state_id = 7
        messages.warning(request, '商品庫存不足，已拒絕交易')
    elif order.order_state_id == 2 and action == 'reject_user':
        order.order_state_id = 8
        messages.warning(request, '已拒絕此用戶交易')
    elif order.order_state_id == 4 and action == 'shipped':
        order.order_state_id = 5
        messages.success(request, '訂單已出貨')
    else:
        messages.error(request, '操作無效或狀態錯誤')
        return redirect('seller_order_detail', order_id=order.id)

    order.save()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'home'
    return redirect(next_url)
# -------------------------
# 賣家批量訂單狀態修改
# -------------------------
@require_POST
@login_required
def batch_seller_action(request):
    VALID_SELLER_ACTIONS = {
    'confirm_order': {'from_state': 2, 'to_state': 3},
    'reject_stock': {'from_state': 2, 'to_state': 7},
    'reject_user': {'from_state': 2, 'to_state': 8},
    'shipped': {'from_state': 4, 'to_state': 5},
    
    }
    action = request.POST.get('action')
    order_ids = request.POST.getlist('order_ids')

    if action not in VALID_SELLER_ACTIONS:
        messages.error(request, '此操作不支援批量處理')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    from_state = VALID_SELLER_ACTIONS[action]['from_state']
    to_state = VALID_SELLER_ACTIONS[action]['to_state']

    success_count = 0
    for oid in order_ids:
        try:
            order = Order.objects.select_related('shop').get(id=oid)
        except Order.DoesNotExist:
            continue
        if order.shop.owner != request.user:
            continue
        if order.order_state_id != from_state:
            continue

        order.order_state_id = to_state
        order.save()
        success_count += 1

    if success_count:
        messages.success(request, f'成功處理 {success_count} 筆訂單')
    else:
        messages.warning(request, '沒有符合條件的訂單被處理')

    return redirect(request.META.get('HTTP_REFERER', 'home'))
