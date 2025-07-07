from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Sum,Prefetch
from collections import defaultdict
from django.utils import timezone
from django.urls import reverse

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .rush_view import maybe_extend_rush
from ..models import *
from ..forms import *
from ..utils import *
# -------------------------
# 購物車查看
# -------------------------
@login_required(login_url='login')
def view_cart(request):
    # 抓取使用者購物車
    cart_items = (
        Cart.objects
        .filter(user=request.user)
        .select_related('product__shop')
        .prefetch_related(
            Prefetch('product__images', queryset=ShopImg.objects.filter(is_cover=True))
        )
    )
    cart_data = []
    shop_latest_update = {}

    for item in cart_items:
        product = item.product
        shop = product.shop

        is_out_of_stock = product.stock <= 0

        shop_id = shop.id
        if shop_id not in shop_latest_update or item.update > shop_latest_update[shop_id]:
            shop_latest_update[shop_id] = item.update

        cart_data.append({
            'shop': shop,
            'product': product,
            'cart': item,
            'is_out_of_stock': is_out_of_stock, #是否超出庫存
            'is_shop_closed': shop.is_end,  #商店是否關閉
        })

    grouped_data = defaultdict(list)
    for entry in cart_data:
        grouped_data[entry['shop'].id].append(entry)

    sorted_shop_ids = sorted(grouped_data.keys(), key=lambda sid: shop_latest_update[sid], reverse=True)

    grouped_cart = []
    for shop_id in sorted_shop_ids:
        items = grouped_data[shop_id]
        items.sort(key=lambda x: (x['is_out_of_stock'], x['product'].id))
        grouped_cart.append({
            'shop': items[0]['shop'],
            'items': items
        })

    return render(request, 'cart.html', {'grouped_cart': grouped_cart})
# -------------------------
# 購物車多商品下單
# -------------------------
@login_required(login_url='login')
def handle_cart_order_creation(request, form, cart_items):
    shop_ids = request.POST.getlist('shop_ids')

    for shop_id in shop_ids:
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            messages.error(request, f'商店 {shop_id} 不存在')
            continue
        if shop.is_end:
            messages.error(request, f'{shop.name} 商店已截止，無法下單')
            continue

        # 該商店的購物車商品
        shop_cart_items = [item for item in cart_items if item.product.shop.id == shop.id]
        if not shop_cart_items:
            messages.warning(request, f'{shop.name} 無商品可購買')
            continue

        shop_form = OrderForm(request.POST, user=request.user, shop=shop)

        if not shop_form.is_valid():
            messages.error(request, f'{shop.name} 表單無效')
            continue

        address = shop_form.cleaned_data['address']
        payment_method_choice = shop_form.cleaned_data['payment_method']
        payment_mode = shop_form.cleaned_data.get('payment_mode')

        if shop.purchase_priority_id != 1:
            shop = maybe_extend_rush(shop)
            intent, _ = PurchaseIntent.objects.get_or_create(user=request.user, shop=shop)
            for item in shop_cart_items:
                product = item.product
                quantity = item.amount
                intent_product, created = IntentProduct.objects.get_or_create(intent=intent, product=product)

                current_total = IntentProduct.objects.filter(product=product).exclude(id=intent_product.id).aggregate(
                    total=Sum('quantity')
                )['total'] or 0
                available_qty = max(product.stock - current_total, 0)

                if created:
                    intent_product.quantity = min(quantity, available_qty)
                else:
                    intent_product.quantity = min(intent_product.quantity + quantity, available_qty)
                intent_product.save()

                if quantity > available_qty:
                    messages.warning(request, f'{product.name} 庫存不足，已調整為 {available_qty} 件')

            Cart.objects.filter(id__in=[c.id for c in shop_cart_items]).delete()
            messages.success(request, f'{shop.name} 的搶購申請已登記')
            continue

        try:
            with transaction.atomic():
                total_price = 0
                locked_products = []

                for item in shop_cart_items:
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    quantity = item.amount
                    if product.stock < quantity:
                        messages.error(request, f'{product.name} 庫存不足')
                        raise Exception(f'{product.name} 庫存不足') 

                    product.stock = F('stock') - quantity
                    product.save()
                    locked_products.append((product, quantity))
                    total_price += product.price * quantity

                if str(payment_method_choice) == '1':
                    pay_state = 1
                    payment_mode = 'full'
                else:
                    if payment_mode == 'deposit':
                        pay_state = 2
                    else:
                        pay_state = 8

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
                for product, qty in locked_products:
                    ProductOrder.objects.create(
                        order=order,
                        product=product,
                        amount=qty,
                    )

                Cart.objects.filter(id__in=[c.id for c in shop_cart_items]).delete()
                messages.success(request, f'{shop.name} 訂單建立成功')
                return redirect(f"{reverse('order_list')}?state=2")

        except Exception as e:
            messages.error(request, f'{shop.name} 下單失敗：{str(e)}')
            return redirect('cart')
# -------------------------
# 加入購物車
# -------------------------
@login_required(login_url='login')
@product_exists_and_not_own_shop_required
def add_to_cart(request, product):
    if product.shop.is_end:
        messages.error(request, "該商店已截止")
        return redirect('shop_by_id', shop_id=product.shop.id)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            messages.error(request, "數量必須大於0")
            return redirect('shop_by_id', shop_id=product.shop.id)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('shop_by_id', shop_id=product.shop.id)

    cart = Cart(user=request.user)
    cart.add_or_update_product(product, quantity)
    messages.success(request, f'成功將 {product.name} 加入購物車')

    return redirect('shop_by_id', shop_id=product.shop.id)
# -------------------------
# 移除購物車
# -------------------------
@login_required(login_url='login')
@cart_exists_required
def delete_cart_item(request, cart_item):
    cart_item.delete()
    messages.success(request, f'{cart_item.product.name} 已從購物車移除')
    return redirect('cart')

@login_required(login_url='login')
def delete_multiple_cart_items(request):
    if request.method == 'POST':
        cart_ids = request.POST.getlist('cart_ids')  # 前端傳來勾選的 cart_id list
        Cart.objects.filter(id__in=cart_ids, user=request.user).delete()
        messages.success(request, '已成功移除選取的商品')
    return redirect('cart')
# -------------------------
# 修改數量
# -------------------------
@login_required(login_url='login')
@cart_exists_required
def update_cart_quantity(request, cart_item):
    if cart_item.product.shop.is_end:
        messages.error(request, "該商店已截止，無法修改商品數量")
        return redirect('cart')
    
    try:
        new_qty = int(request.POST.get('quantity', 1))
    except ValueError:
        messages.error(request, "輸入的數量無效")
        return redirect('cart')

    if new_qty <= 0:
        messages.error(request, "數量必須大於 0")
        return redirect('cart')

    other_cart_qty = (
        Cart.objects.filter(product=cart_item.product)
        .exclude(id=cart_item.id)
        .aggregate(total=Sum('amount'))['total'] or 0
    )
    available_stock = cart_item.product.stock - other_cart_qty

    if new_qty > available_stock:
        messages.warning(request, f'{cart_item.product.name} 最多只能購買 {available_stock} 件')
        cart_item.amount = available_stock
    else:
        cart_item.amount = new_qty

    cart_item.update = timezone.now()
    cart_item.save()
    messages.success(request, f'{cart_item.product.name} 數量已更新為 {cart_item.amount}')
    return redirect('cart')