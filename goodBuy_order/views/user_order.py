from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .rush_view import maybe_extend_rush
from ..models import *
from ..forms import *
from ..utils import *

# -------------------------
# 單商品下單
# -------------------------
@login_required(login_url='login')
@product_exists_and_not_own_shop_required
def purchase_single_product(request, product):
    shop = product.shop
    quantity = int(request.POST.get('quantity', 1))
    
    if shop.is_end:
        messages.error(request, '商店已結束營業')
        return redirect('商店界面', shop_id=shop.id)
    # --------------------------
    # 搶購處理：僅建立 Intent
    # --------------------------
    if shop.purchase_priority_id != 1:
        shop = maybe_extend_rush(shop)
        intent, _ = PurchaseIntent.objects.get_or_create(user=request.user, shop=shop)
        intent_product, created = IntentProduct.objects.get_or_create(intent=intent, product=product)

        user_claimed = IntentProduct.objects.filter(product=product,intent__user=request.user,intent__shop=shop).aggregate(total=Sum('quantity'))['total'] or 0

        available_qty = max(product.stock - user_claimed, 0)

        if intent_product.quantity + quantity > available_qty:
            messages.warning(request, f'你已多帶 {user_claimed} 件，最多只可購買 {available_qty} 件')
            quantity = max(available_qty - intent_product.quantity, 0)

        if quantity <= 0:
            messages.warning(request, f'{product.name} 以無庫存')
        else:
            intent_product.quantity += quantity
            intent_product.save()
            msg = '商品已加入多帶列表' if created else f'數量已累加至 {intent_product.quantity} 件'
            messages.success(request, msg)

        return redirect('product_detail', product_id=product.id)

    # --------------------------
    # 一般購買流程
    # --------------------------
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user, shop=shop)
        if form.is_valid():
            address = form.cleaned_data['address']
            payment_method_choice = form.cleaned_data['payment_method']
            payment_mode = form.cleaned_data.get('payment_mode')

            try:
                with transaction.atomic():
                    # 鎖定商品，避免並行更新
                    locked_product = Product.objects.select_for_update().get(id=product.id)
                    if locked_product.stock < quantity:
                        messages.error(request, '庫存不足')
                        return redirect('商店界面', shop_id=shop.id)

                    locked_product.stock = F('stock') - quantity
                    locked_product.save()

                    total_price = locked_product.price * quantity

                    # 設定支付方式與狀態文字
                    if str(payment_method_choice) == '1':
                        pay_state = 1
                        payment_mode = 'full'
                    else:
                        if payment_mode == 'deposit':
                            pay_state = 2
                        else:
                            pay_state = 8

                    # 建立訂單
                    order = Order.objects.create(
                        user=request.user,
                        shop=shop,
                        total=total_price,
                        address=address,
                        payment_category=payment_method_choice,
                        payment_mode=payment_mode,
                        pay_state_id=PayState.objects.get(id=pay_state),
                        order_state_id=1,
                        second_supplement=0,
                        pay=None
                    )

                    # 建立商品項目
                    ProductOrder.objects.create(
                        order=order,
                        product=locked_product,
                        amount=quantity,
                    )

                    messages.success(request, '下單成功')
                    return redirect('order_detail', order_id=order.id)

            except Exception as e:
                messages.error(request, f'下單失敗：{e}')

    else:
        form = OrderForm(user=request.user, shop=shop)

    return render(request, 'quick_purchase.html', locals())
# -------------------------
# 買家選擇付款方式
# -------------------------
def choose_payment_method(order, request=None):
    if order.order_state_id != 1:
        messages.error(request, '訂單狀態錯誤，無法選擇付款方式')
        return redirect('buyer_order_detail', order_id=order.id)
    
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
def upload_payment_proof(order, request=None):
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
