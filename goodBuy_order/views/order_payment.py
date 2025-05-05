from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from goodBuy_order.models import Order
from goodBuy_shop.models import ShopPayment
from django.shortcuts import redirect, render

from ..forms import OrderPaymentForm
from utils import order_buyer_required, order_seller_required
# -------------------------
# 買家選擇付款方式
# -------------------------
@login_required
@order_buyer_required(redirect_to='buyer_order_list')
def choose_payment_method(request, order):
    shop = order.shop
    shop_payment_links = ShopPayment.objects.filter(shop=shop).select_related('payment_account')

    available_payment_methods = []
    remittance_accounts = []

    if shop.transfer:
        remittance_accounts = shop_payment_links.exclude(payment_account__id=1)
        if remittance_accounts.exists():
            available_payment_methods.append('remittance')

        if shop_payment_links.filter(payment_account__id=1).exists():
            available_payment_methods.append('cash_on_delivery')
    else:
        available_payment_methods.append('cash_on_delivery')

    if not available_payment_methods:
        messages.error(request, '此商店未設定任何可用付款方式')
        return redirect('buyer_order_detail', order_id=order.id)

    if request.method == 'POST':
        selected_method = request.POST.get('payment_method')

        if selected_method not in available_payment_methods:
            messages.error(request, '付款方式無效')
            return redirect('order_payment_choice', order_id=order.id)

        order.payment_category = selected_method

        if selected_method == 'remittance':
            try:
                selected_account_id = int(request.POST.get('payment_account_id'))
            except (TypeError, ValueError, ShopPayment.DoesNotExist):
                messages.error(request, '請選擇有效的匯款帳戶')
                return redirect('order_payment_choice', order_id=order.id)

        order.order_state_id = 2
        order.save()

        messages.success(request, '付款方式已選擇')
        return redirect('buyer_order_detail', order_id=order.id)

    return render(request, 'order/payment_choice.html', locals())
# -------------------------
# 買家上傳付款憑證
# -------------------------
@login_required
@order_buyer_required(redirect_to='buyer_order_list')
def upload_payment_proof(request, order):
    if order.payment_category != 'remittance':
        messages.error(request, '此訂單不需匯款，無法上傳憑證')
        return redirect('buyer_order_detail', order_id=order.id)

    if order.has_pending_payment_proof:
        messages.error(request, '您已上傳付款憑證，請等待賣家確認或退回後再試')
        return redirect('buyer_order_detail', order_id=order.id)

    remit_accounts = ShopPayment.objects.filter(shop=order.shop).exclude(payment_account__id=1)

    if request.method == 'POST':
        form = OrderPaymentForm(request.POST, request.FILES)
        account_id = request.POST.get('payment_account_id')

        if not account_id:
            messages.error(request, '請選擇匯款帳戶')
            return redirect('buyer_order_detail', order_id=order.id)

        try:
            shop_payment = remit_accounts.get(id=account_id)
        except ShopPayment.DoesNotExist:
            messages.error(request, '匯款帳戶無效')
            return redirect('buyer_order_detail', order_id=order.id)

        if form.is_valid():
            payment_record = form.save(commit=False)
            payment_record.order = order
            payment_record.shop_payment = shop_payment
            payment_record.is_paid_by_user = True
            payment_record.seller_state = 'wait_confirmed'
            payment_record.save()

            messages.success(request, '匯款資訊已上傳，等待賣家確認')
            return redirect('buyer_order_detail', order_id=order.id)
        else:
            messages.error(request, '表單內容有誤，請重新確認')
    else:
        form = OrderPaymentForm()

    return render(request, 'order/upload_payment.html', locals())

# -------------------------
# 賣家查看付款憑證
# -------------------------

# -------------------------
# 賣家確認/拒絕付款憑證
# -------------------------