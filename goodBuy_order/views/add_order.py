# 購買邏輯 view：處理三種下單方式
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
            messages.warning(request, f'{product.name} 的剩餘可購買數量不足')
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
            payment_account = form.cleaned_data.get('payment_account')

            # 付款防呆：匯款但沒選帳號
            if str(payment_method_choice) != '1' and not payment_account:
                messages.error(request, '請選擇匯款帳戶')
                return redirect('商店界面', shop_id=shop.id)

            if quantity > product.stock:
                messages.error(request, '庫存不足')
                return redirect('商店界面', shop_id=shop.id)

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
                        payment_method_text = '取貨付款'
                        pay_state = 1
                        payment_mode = 'full'
                        payment_account = None
                    else:
                        payment_obj = Payment.objects.get(id=payment_method_choice)
                        payment_method_text = f'匯款 - {payment_obj.name}'
                        if payment_mode == 'deposit':
                            pay_state = 2  # 待支付定金
                        else:
                            pay_state = 8  # 全額匯款

                    # 建立訂單
                    order = Order.objects.create(
                        user=request.user,
                        shop=shop,
                        shop_name=shop.name,
                        total=total_price,
                        address=address,
                        payment=payment_account,
                        payment_method=payment_method_text,
                        payment_mode=payment_mode,
                        pay_state_id=pay_state,
                        order_state_id=1,
                        second_supplement=0,
                        pay=None
                    )

                    # 建立商品項目
                    ProductOrder.objects.create(
                        order=order,
                        product=locked_product,
                        amount=quantity,
                        product_name=locked_product.name,
                        product_price=locked_product.price,
                        product_img=locked_product.img.name if locked_product.img else ''
                    )

                    messages.success(request, '下單成功')
                    return redirect('order_detail', order_id=order.id)

            except Exception as e:
                messages.error(request, f'下單失敗：{e}')

    else:
        form = OrderForm(user=request.user, shop=shop)

    return render(request, 'quick_purchase.html', locals())
# -------------------------
# 多商品購買（依商店群組，若為搶購則記錄 IntentProduct）
# -------------------------
@login_required(login_url='login')
def purchase_from_cart(request):
    if request.method == 'POST':
        form = OrderForm(request.POST, user=request.user)
        product_ids = request.POST.getlist('product_ids')  # 多個商品
        if not product_ids:
            messages.warning(request, '請選擇至少一項商品')
            return redirect('cart')

        products = Product.objects.filter(id__in=product_ids).select_related('shop')
        shop_groups = {}
        for p in products:
            shop_groups.setdefault(p.shop.id, []).append(p)

        for shop_id, shop_products in shop_groups.items():
            shop = shop_products[0].shop
            form = OrderForm(request.POST, user=request.user, shop=shop)

            if form.is_valid():
                address = form.cleaned_data['address']
                payment_method_choice = form.cleaned_data['payment_method']
                payment_mode = form.cleaned_data.get('payment_mode')
                payment_account = form.cleaned_data.get('payment_account')

                # 多帶先加入多帶表，不創建訂單
                if shop.purchase_priority_id != 1:
                    intent, _ = PurchaseIntent.objects.get_or_create(user=request.user, shop=shop)
                    for p in shop_products:
                        qty = int(request.POST.get(f'quantity_{p.id}', 1))
                        intent_product, _ = IntentProduct.objects.get_or_create(intent=intent, product=p)

                        # 計算其他人已搶購的總數
                        current_total = IntentProduct.objects.filter(product=p).exclude(intent=intent).aggregate(
                            total=Sum('quantity')
                        )['total'] or 0

                        available_qty = max(p.stock - current_total, 0)
                        old_qty = intent_product.quantity

                        # 本次允許的增加量
                        allow_add = min(qty, available_qty - old_qty)
                        if allow_add <= 0:
                            messages.warning(request, f"{p.name} 多帶數量已達上限，無法再增加")
                            continue

                        intent_product.quantity = old_qty + allow_add
                        intent_product.save()

                        Cart.objects.filter(user=request.user, product__in=shop_products).delete()
                        
                        if allow_add < qty:
                            messages.info(request, f"{p.name} 只成功加入 {allow_add} 件（已達上限）")
                        else:
                            messages.success(request, f"{p.name} 數量已累加至 {intent_product.quantity} 件")
                    continue

                total_price = 0
                try:
                    with transaction.atomic():
                        for p in shop_products:
                            qty = int(request.POST.get(f'quantity_{p.id}', 1))
                            product = Product.objects.select_for_update().get(id=p.id)
                            if product.stock < qty:
                                messages.error(request, f'{product.name} 庫存不足')
                                return redirect('cart')

                            product.stock = F('stock') - qty
                            product.save()
                            total_price += product.price * qty

                        if payment_method_choice == '1':  # 取貨付款
                            payment_method_text = '取貨付款'
                            pay_state = 1
                            payment_mode = 'full'
                            payment_account = None
                        else:  # 匯款
                            payment_method_text = f'匯款 - {payment_account.payment.name}'
                            if payment_mode == 'deposit':
                                pay_state = 2  # 待支付定金
                            else:
                                pay_state = 8  # 全額匯款

                        order = Order.objects.create(
                            user=request.user,
                            shop=shop,
                            shop_name=shop.name,
                            total=total_price,
                            address=address,
                            payment=payment_account,
                            payment_method=payment_method_text,
                            payment_mode=payment_mode,
                            pay_state_id=pay_state,
                            order_state_id=1,
                            second_supplement=0,
                            pay=None
                        )

                        # 建立商品明細
                        for p in shop_products:
                            qty = int(request.POST.get(f'quantity_{p.id}', 1))
                            ProductOrder.objects.create(
                                order=order,
                                product=p,
                                amount=qty,
                                product_name=p.name,
                                product_price=p.price,
                                product_img=p.img.name if p.img else '',
                            )

                        Cart.objects.filter(user=request.user, product__in=products).delete()
                        messages.success(request, f'{shop.name} 訂單建立成功')

                except Exception as e:
                    messages.error(request, f'{shop.name} 下單失敗：{e}')

        return redirect('order_list')

    else:
        form = OrderForm(user=request.user)

    return render(request, 'order_form.html', {'form': form})
