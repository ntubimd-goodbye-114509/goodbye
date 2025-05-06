from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from goodBuy_order.models import Order, OrderPayment
from goodBuy_shop.models import ShopPayment
from django.shortcuts import redirect, render

from ..forms import OrderPaymentForm
from .order_payment import *
from .user_order import *
from utils import order_buyer_required, order_seller_required
# -------------------------
# 庫存退回
# -------------------------
def restore_order_stock(order):
    for item in order.items.select_related('product'):
        item.product.stock += item.quantity
        item.product.save()
# -------------------------
# 訂單狀態修改 - ex. 付款、出貨
# -------------------------
# 買家訂單狀態修改
# -------------------------
@order_buyer_required(redirect_to='buyer_order_list')
def buyer_action(request, order):
    action = request.POST.get('action')
    if order.order_state_id == 1 and action == 'chosen_payment':
        choose_payment_method(order, request)

    elif order.order_state_id in [1, 2] and action == 'cancel_order':
        order.order_state_id = 11
        restore_order_stock(order)
        messages.warning(request, '訂單已取消')

    elif order.order_state_id == 3 and action == 'need_pay':
        upload_payment_proof(order, request)

    elif order.order_state_id == 5 and action == 'confirm_received':
        if order.payment_category == 'cash_on_delivery' and not order.payments.exists():
            OrderPayment.objects.create(
                order=order,
                amount=order.total + (order.second_supplement or 0),
                is_paid_by_user=True,
                seller_state='none',
                remark='取貨付款自動記錄',
            )
        messages.success(request, '已確認收貨')
        order.pay_state_id = 6
    
    else:
        messages.error(request, '操作無效或狀態錯誤')
        return redirect(request.META.get('HTTP_REFERER') or 'home')

    order.save()
    return redirect('buyer_order_list')
# -------------------------
# 賣家訂單狀態修改
# -------------------------
@order_seller_required(redirect_to='seller_order_list')
def seller_action(request, order):
    action = request.POST.get('action')

    if order.order_state_id == 2 and action == 'confirm_order':
        if order.payment_category == 'cash_on_delivery':
            order.order_state_id = 4
        else:
            order.order_state_id = 3
        messages.success(request, '訂單已確認')

    elif order.order_state_id == 3 and action == 'notify_payment':
        if not notify_buyer_to_pay(order, request):
            return redirect('seller_order_detail', order_id=order.id)
    
    elif order.order_state_id == 2 and action == 'reject_stock':
        order.order_state_id = 7
        restore_order_stock(order)
        messages.warning(request, '商品庫存不足，已拒絕交易')
    
    elif order.order_state_id == 2 and action == 'reject_user':
        order.order_state_id = 8
        restore_order_stock(order)
        messages.warning(request, '已拒絕此用戶交易')
    
    elif order.order_state_id == 2 and action == 'reject_unsuccessful':
        order.order_state_id = 10
        restore_order_stock(order)
        messages.warning(request, '已告知用戶流團')
    
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
        'shipped': {'from_state': 4, 'to_state': 5},
        'notify_payment': None,
    }

    action = request.POST.get('action')
    order_ids = request.POST.getlist('order_ids')

    if action not in VALID_SELLER_ACTIONS:
        messages.error(request, '此操作不支援批量處理')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    success_count = 0

    for oid in order_ids:
        try:
            order = Order.objects.select_related('shop').get(id=oid)
        except Order.DoesNotExist:
            continue
        if order.shop.owner != request.user:
            continue

        if action == 'notify_payment':
            if order.order_state_id == 3 and notify_buyer_to_pay(order):
                order.save()
                success_count += 1
            continue

        from_state = VALID_SELLER_ACTIONS[action]['from_state']
        to_state = VALID_SELLER_ACTIONS[action]['to_state']

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
