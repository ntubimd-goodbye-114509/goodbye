from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Sum, OuterRef, Subquery
from django.shortcuts import redirect, render

from ..forms import SecondSupplementForm
from utils import *
# -------------------------
# 查看付款憑證 - 單筆
# -------------------------
@login_required
@order_exists_required
def view_order_payment_history(request, order):

    is_seller = (order.shop.owner == request.user)
    is_buyer = (order.user == request.user)   
    
    if not (is_seller or is_buyer):
        messages.error(request, '你沒有權限查看這筆訂單的付款紀錄')
        return redirect('home')
    
    if order.payment_category == 'cash_on_delivery':
        messages.error(request, '貨到付款訂單無法查看付款紀錄')
        return redirect('home')
    
    payments = order.payments.order_by('-pay_time')

    latest_payment = payments.first() if payments.exists() else None

    return render(request, 'view_payment_proofs.html', locals())
# -------------------------
# 查看付款憑證 - 多筆 - 可商店查詢
# -------------------------
@login_required
def list_related_payments(request):
    user = request.user
    action = request.GET.get('action')
    buyer_or_seller = request.GET.get('buyer_or_seller')
    shop_id = request.GET.get('shop_id')

    confirmed_total = waiting_total = None

    if buyer_or_seller == 'buyer':
        payments = OrderPayment.objects.filter(
            order__user=user
        ).exclude(seller_state='none').order_by('-pay_time')

    elif buyer_or_seller == 'seller':
        payments = OrderPayment.objects.filter(
            order__shop__owner=user
        ).exclude(seller_state='none').order_by('-pay_time')

        if shop_id:
            try:
                shop = Shop.objects.get(id=shop_id, owner=user)
            except Shop.DoesNotExist:
                messages.error(request, '你無權查看這家商店的付款紀錄')
                return redirect('home')
            payments = payments.filter(order__shop=shop)

        confirmed_total = payments.filter(seller_state='confirmed').aggregate(Sum('amount'))['amount__sum'] or 0
        waiting_total = payments.filter(seller_state='wait confirmed').aggregate(Sum('amount'))['amount__sum'] or 0
    else:
        messages.error(request, '查詢權限錯誤')
        return redirect('home') 

    if action == 'wait_confirmed':
        payments = payments.filter(seller_state='wait confirmed')
    elif action == 'confirmed':
        payments = payments.filter(seller_state='confirmed')
    elif action == 'cancel':
        payments = payments.filter(seller_state__in=['returned', 'overdue'])

    latest_payment_per_order = OrderPayment.objects.filter(
        order=OuterRef('order')
    ).order_by('-pay_time')

    payments = payments.filter(
        id=Subquery(latest_payment_per_order.values('id')[:1])
    ).order_by('-pay_time')

    return render(request, 'payment_list_all.html', locals())
# -------------------------
# 賣家確認/拒絕付款憑證
# -------------------------
@require_POST
@order_payment_owner_required
def audit_payment(request, payment):
    action = request.POST.get('action')

    if payment.seller_state != 'wait confirmed':
        messages.warning(request, '這筆付款已處理過')
        return redirect('view_payment_proofs', order_id=payment.order.id)

    if action == 'confirm':
        payment.seller_state = 'confirmed'
        payment.remark = request.POST.get('remark', '') or payment.remark
        messages.success(request, '已確認收款')

    elif action == 'reject':
        payment.seller_state = 'returned'
        payment.remark = request.POST.get('remark', '') or payment.remark
        messages.success(request, '已退回憑證')

    else:
        messages.error(request, '無效的操作')

    payment.save()
    return redirect('view_payment_proofs', order_id=payment.order.id)
# -------------------------
# 賣家通知付款
# -------------------------
def notify_buyer_to_pay(order, request=None):
    current = order.pay_state_id

    if current in [1, 2, 4, 6, 7, 9, 10]:
        if request:
            messages.error(request, '目前付款狀態不允許通知付款')
        return False

    elif current == 3:
        order.pay_state_id = 4
        if request:
            messages.success(request, '已通知買家支付尾款')

    elif current == 5 or current == 8:
        if order.second_supplement and order.second_supplement > 0:
            order.pay_state_id = 6
            if request:
                messages.success(request, '已通知買家支付額外費用')
        else:
            order.pay_state_id = 7
            if request:
                messages.success(request, '已確認買家已支付所有費用')
                order.order_state_id = 4

    elif current == 8:
        order.pay_state_id = 9
        if request:
            messages.success(request, '已確認買家完成全額付款')
            
    order.save()
    return True
# -------------------------
# 賣家設定二次補款
# -------------------------
@order_seller_required
def set_second_supplement(request, order):
    if request.method == 'POST':
        form = SecondSupplementForm(request.POST)
        if form.is_valid():
            order.second_supplement = form.cleaned_data['second_supplement']
            order.save()

            messages.success(request, '補款金額已更新')
            return redirect('seller_order_detail', order_id=order.id)
    else:
        form = SecondSupplementForm(initial={'second_supplement': order.second_supplement or 0})

    return render(request, 'set_second_supplement.html', locals())
