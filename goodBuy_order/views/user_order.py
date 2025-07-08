from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum
from collections import defaultdict

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .rush_view import maybe_extend_rush
from ..models import *
from ..forms import *
from ..utils import *
from utils.decorators_shortcuts import *

# -------------------------
# 商品下單
# -------------------------
@login_required(login_url='login')
def checkout(request):
    cart_ids = request.POST.getlist('cart_ids') if request.method == 'POST' else []
    product_id = request.GET.get('product_id')
    quantity = int(request.GET.get('quantity', 1))

    shop_groups = defaultdict(list)
    cart_items = []
    single_product = None

    # 單品快速下單（來源為 GET）
    if product_id:
        product = get_object_or_404(Product, id=product_id, is_delete=False)
        shop = product.shop
        shop_groups[shop].append({'product': product, 'quantity': quantity})
        single_product = product

    # 購物車下單（來源為 POST）
    elif cart_ids:
        cart_items = Cart.objects.select_related('product__shop').filter(id__in=cart_ids, user=request.user)
        if not cart_items:
            messages.error(request, '購物車資料無效')
            return redirect('cart')

        for item in cart_items:
            product = item.product
            shop_groups[product.shop].append({'product': product, 'quantity': item.amount})

    else:
        messages.error(request, '無有效商品')
        return redirect('cart')

    orders_created = []
    if request.method == 'POST' and 'checkout_submit' in request.POST:
        # 為每間 shop 處理一次下單流程
        for shop, items in shop_groups.items():
            if shop.is_end:
                messages.error(request, f'{shop.name} 商店已結束營業')
                continue

            form = OrderForm(request.POST, user=request.user, shop=shop)
            if not form.is_valid():
                messages.error(request, f'{shop.name} 的表單驗證失敗')
                continue

            address = form.cleaned_data['address']
            payment_method = form.cleaned_data['payment_method']
            payment_mode = form.cleaned_data.get('payment_mode')

            # 搶購流程
            if shop.purchase_priority_id != 1:
                shop = maybe_extend_rush(shop)
                intent, _ = PurchaseIntent.objects.get_or_create(user=request.user, shop=shop)

                for item in items:
                    product = item['product']
                    qty = item['quantity']
                    intent_product, created = IntentProduct.objects.get_or_create(intent=intent, product=product)

                    current_total = IntentProduct.objects.filter(product=product).exclude(id=intent_product.id).aggregate(
                        total=Sum('quantity')
                    )['total'] or 0
                    available_qty = max(product.stock - current_total, 0)

                    if created:
                        intent_product.quantity = min(qty, available_qty)
                    else:
                        intent_product.quantity = min(intent_product.quantity + qty, available_qty)

                    intent_product.save()

                    if qty > available_qty:
                        messages.warning(request, f'{product.name} 庫存不足，已調整為 {available_qty} 件')

                messages.success(request, f'{shop.name} 多帶商品已加入')
                continue

            # 一般建立訂單流程
            try:
                with transaction.atomic():
                    total = 0
                    locked_products = []

                    for item in items:
                        product = Product.objects.select_for_update().get(id=item['product'].id)
                        qty = item['quantity']
                        if product.stock < qty:
                            raise Exception(f'{product.name} 庫存不足')
                        product.stock = F('stock') - qty
                        product.save()
                        total += product.price * qty
                        locked_products.append((product, qty))

                    if payment_method == 'cash_on_delivery':
                        pay_state = 1
                        payment_mode = 'full'
                    else:
                        pay_state = 2 if payment_mode == 'deposit' else 8

                    order = Order.objects.create(
                        user=request.user,
                        shop=shop,
                        total=total,
                        address=address,
                        payment_category=payment_method,
                        payment_mode=payment_mode,
                        pay_state_id=PayState.objects.get(id=pay_state),
                        order_state_id=1,
                        second_supplement=0,
                        pay=None
                    )

                    for product, qty in locked_products:
                        ProductOrder.objects.create(order=order, product=product, amount=qty)

                    orders_created.append(order)
                    messages.success(request, f'{shop.name} 訂單已建立')
            except Exception as e:
                messages.error(request, f'{shop.name} 下單失敗：{e}')

        # 清除購物車項目
        if cart_items:
            cart_items.delete()

        if orders_created:
            return redirect('order_list')

    # 顯示頁面（GET）
    form_by_shop = {shop: OrderForm(user=request.user, shop=shop) for shop in shop_groups}

    return render(request, 'checkout.html', {
        'shop_groups': shop_groups,
        'form_by_shop': form_by_shop,
        'single_product': single_product,
    })

# -------------------------
# 買家選擇付款方式
# -------------------------
@login_required(login_url='login')
@order_buyer_required
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

    return render(request, 'payment_choice.html', {'available_payment_methods': available_payment_methods,
                                                'remittance_accounts': remittance_accounts,})

# -------------------------
# 買家上傳付款憑證
# -------------------------
@login_required(login_url='login')
@order_buyer_required
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

    return render(request, 'upload_payment.html', {'remit_accounts':remit_accounts,
                                                    'form': form,
                                                    'order': order})
