# 購買邏輯 view：處理三種下單方式
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum

from goodBuy_shop.models import *
from goodBuy_web.models import *
from ..models import *
from ..order_forms import *

# -------------------------
# 單一商品購買（若為搶購則記錄 IntentProduct）
# -------------------------
@login_required(login_url='login')
def purchase_single_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    shop = product.shop
    quantity = int(request.POST.get('quantity', 1))

    if shop.purchase_priority_id != 1:
        intent, _ = PurchaseIntent.objects.get_or_create(user=request.user, shop=shop)
        intent.add_or_update_product(product, quantity)
        messages.success(request, '商品已加入搶購登記')
        return redirect('product_detail', product_id=product.id)

    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        payment_id = request.POST.get('payment')

        if quantity > product.stock:
            messages.error(request, '庫存不足')
            return redirect('product_detail', product_id=product.id)

        try:
            with transaction.atomic():
                locked_product = Product.objects.select_for_update().get(id=product.id)
                if locked_product.stock < quantity:
                    messages.error(request, '庫存不足')
                    return redirect('product_detail', product_id=product.id)

                locked_product.stock = F('stock') - quantity
                locked_product.save()

                payment_method_obj = get_object_or_404(Payment, id=payment_method_id)

                total_price = product.price * quantity

                order = Order.objects.create(
                    user=request.user,
                    shop=shop,
                    shop_name=shop.name,
                    total=total_price,
                    payment_method=payment_method_obj.name,
                    payment=PaymentAccount.objects.get(id=payment_id) if payment_method_obj.name == '匯款' and payment_id else None,
                    pay_state_id=1 if payment_method_obj.name == '貨到付款' else 2,
                    order_state_id=2 if shop.purchase_priority_id in [2, 3] else 1,
                    second_supplement=0,
                    pay=None
                )

                ProductOrder.objects.create(
                    order=order,
                    product=product,
                    amount=quantity,
                    product_name=product.name,
                    product_price=product.price,
                    product_img=product.img.name if product.img else ''
                )

                # 判斷是否為定金制
                if shop.deposit:
                    OrderPayment.objects.create(order=order, amount=total_price // 2, is_deposit=True)
                else:
                    OrderPayment.objects.create(order=order, amount=total_price, is_deposit=True)

                messages.success(request, '下單成功')
                return redirect('order_detail', order_id=order.id)

        except Exception as e:
            messages.error(request, f'下單失敗：{e}')

    return render(request, 'quick_purchase.html', locals())


# -------------------------
# 多商品購買（依商店群組，若為搶購則記錄 IntentProduct）
# -------------------------
@login_required(login_url='login')
def purchase_from_cart(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        product_ids = request.POST.getlist('product_ids')
        payment_method_id = request.POST.get('payment_method')
        payment_id = request.POST.get('payment')

        if form.is_valid() and product_ids:
            products = Product.objects.filter(id__in=product_ids)
            shop_groups = {}
            for p in products:
                shop_groups.setdefault(p.shop.id, []).append(p)

            for shop_id, shop_products in shop_groups.items():
                shop = shop_products[0].shop

                if shop.purchase_priority_id != 1:
                    intent, _ = PurchaseIntent.objects.get_or_create(user=request.user, shop=shop)
                    for p in shop_products:
                        qty = int(request.POST.get(f'quantity_{p.id}', 1))
                        intent.add_or_update_product(p, qty)
                    continue

                order = form.save(commit=False)
                order.user = request.user
                order.shop = shop
                order.shop_name = shop.name
                order.total = 0
                order.second_supplement = 0

                payment_method_obj = get_object_or_404(Payment, id=payment_method_id)
                if payment_method_obj.name == '匯款' and payment_id:
                    order.payment = get_object_or_404(PaymentAccount, id=payment_id)
                order.payment_method = payment_method_obj.name
                order.pay_state_id = 1 if payment_method_obj.name == '貨到付款' else 2
                order.order_state_id = 2 if shop.purchase_priority_id in [2, 3] else 1

                order.save()

                total_price = 0
                for p in shop_products:
                    qty = int(request.POST.get(f'quantity_{p.id}', 1))
                    ProductOrder.objects.create(
                        order=order,
                        product=p,
                        amount=qty,
                        product_name=p.name,
                        product_price=p.price,
                        product_img=p.img.name if p.img else ''
                    )
                    total_price += p.price * qty

                order.total = total_price
                order.save()

                if shop.deposit:
                    OrderPayment.objects.create(order=order, amount=total_price // 2, is_deposit=True)
                else:
                    OrderPayment.objects.create(order=order, amount=total_price, is_deposit=True)

            messages.success(request, '訂單建立成功 / 搶購申請已送出')
            return redirect('order_list')

    else:
        form = OrderCreateForm()

    return render(request, 'order_form.html', {'form': form})
