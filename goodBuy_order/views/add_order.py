from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum

from goodBuy_shop.models import *
from goodBuy_web.models import *
from ..models import *
from ..forms import *
from ..utils import *

# -------------------------
@login_required(login_url='login')
@product_exists_and_not_own_shop_required
def purchase_single_product(request, product):
    shop = product.shop
    quantity = int(request.POST.get('quantity', 1))

    # --------------------------
    # 搶購處理：僅建立 Intent
    # --------------------------
    if shop.purchase_priority_id != 1:
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
