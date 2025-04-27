from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

from goodBuy_shop.models import Product,Shop
from goodBuy_order.models import *
from goodBuy_web.models import User

# -------------------------
# 商品是否存在&使用者非商品擁有者
# -------------------------
def product_exists_and_not_own_shop_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, product_id, *args, **kwargs):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, '找不到這個商品呢qwq')
            return redirect('home')
        
        if product.shop.owner == request.user:
            messages.warning(request, '不能下單自己的商品哦')
            return redirect('home') 

        return view_func(request, product, *args, **kwargs)
    return _wrapped_view
# -------------------------
# 帶多邏輯判斷
# -------------------------
def allocate_rush_orders(shop_id):
    shop = Shop.objects.get(id=shop_id)
    if not shop.purchase_priority_id in [2, 3]:
        return

    intents = PurchaseIntent.objects.filter(shop=shop).prefetch_related('intent_products', 'user')

    user_demands = {}
    for intent in intents:
        uid = intent.user_id
        if uid not in user_demands:
            user_demands[uid] = {}
        for ip in intent.intent_products.all():
            user_demands[uid][ip.product_id] = user_demands[uid].get(ip.product_id, 0) + ip.quantity

    product_stock = {p.id: p.stock for p in Product.objects.filter(shop=shop)}
    allocated_users = []  # 成功分配商品的使用者

    if shop.purchase_priority_id == 2:  # 金額高優先
        sorted_users = sorted(user_demands.items(), key=lambda u: sum(
            Product.objects.get(id=pid).price * qty for pid, qty in u[1].items()), reverse=True)
    elif shop.purchase_priority_id == 3:  # 數量多優先
        sorted_users = sorted(user_demands.items(), key=lambda u: sum(qty for qty in u[1].values()), reverse=True)

    for user_id, product_want in sorted_users:
        can_allocate = True
        for pid, qty in product_want.items():
            if product_stock.get(pid, 0) < qty:
                can_allocate = False
                break

        if can_allocate:
            for pid, qty in product_want.items():
                product_stock[pid] -= qty

            user = User.objects.get(id=user_id)
            total_price = sum(Product.objects.get(id=pid).price * qty for pid, qty in product_want.items())

            order = Order.objects.create(
                user=user,
                shop=shop,
                shop_name=shop.name,
                total=total_price,
                order_state_id=1,
                pay_state_id=10,
                payment_method= PayState.objects.get(id=10).name, 
                second_supplement=0
            )

            for pid, qty in product_want.items():
                product = Product.objects.get(id=pid)
                ProductOrder.objects.create(
                    order=order,
                    product=product,
                    amount=qty,
                    product_name=product.name,
                    product_price=product.price,
                    product_img=product.img.name if product.img else ''
                )

            allocated_users.append(user_id)

    return allocated_users
# -------------------------
# 購物車商品存在檢查
# -------------------------
def cart_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, cart_id, *args, **kwargs):
        try:
            cart_item = Cart.objects.get(id=cart_id)
        except:
            messages.error(request, '購物車沒有這個商品呢')
            return redirect('home')

        if cart_item.user != request.user:
            messages.error(request, "這不是你的購物車項目喔")
            return redirect('view_cart')

        return view_func(request, cart_item, *args, **kwargs)
    
    return _wrapped_view
# -------------------------
# 訂單存在檢查
# -------------------------
def order_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)
        except:
            messages.error(request, "訂單不存在")
            return redirect('訂單頁面')
        return view_func(request, order, *args, **kwargs)
    return _wrapped_view
# -------------------------
# 訂單存在+商店主人檢查
# -------------------------
def order_exists_and_shop_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request,shop_id, order_id, *args, **kwargs):
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            messages.error(request, "商店不存在")
            return redirect('home')
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            messages.error(request, "訂單不存在")
            return redirect('訂單列表頁', shop_id=shop.id)
        
        if order.shop != shop:
            messages.error(request, '訂單不屬於此商店')
            return redirect('訂單列表頁', shop_id=shop.id)
        
        if order.shop.owner != request.user:
            messages.error(request, "您無權操控訂單")
            return redirect('home')
        
        return view_func(request,shop, order, *args, **kwargs)
    return _wrapped_view
# -------------------------
# 商店存在+是否為多帶商店檢查
# -------------------------
def shop_exists_and_is_rush_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request,shop_id, *args, **kwargs):
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            messages.error(request, "商店不存在")
            return redirect('home')
        
        if shop.purchase_priority_id not in [2, 3]:
            messages.error(request, "此商店不是搶購模式")
            return redirect('商店', shop_id=shop.id)

        if timezone.now() > shop.end_time and request.user != shop.owner:
            messages.info(request, '多帶已結算')
            return redirect('商店', shop_id=shop.id)
        
        return view_func(request, shop, *args, **kwargs)
    return _wrapped_view
# -------------------------
# 多帶&商店存在檢查
# -------------------------
def rush_exists_and_shop_exist_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, shop_id, purchaseIntent_id, *args, **kwargs):
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            messages.error(request, "商店不存在")
            return redirect('home')
        
        if shop.purchase_priority_id not in [2, 3]:
            messages.error(request, "此商店不是搶購模式")
            return redirect('商店', shop_id=shop.id)

        if timezone.now() > shop.end_time and request.user != shop.owner:
            messages.info(request, '多帶已結算')
            return redirect('商店', shop_id=shop.id)
        try:
            intent = PurchaseIntent.objects.get(id=purchaseIntent_id)
        except PurchaseIntent.DoesNotExist:
            messages.error(request, "您沒有參與這個多帶")
            return redirect('多帶訂單頁面')
        
        if intent.user != request.user:
            messages.error(request, "這不是你的多帶表無法查看")
            return redirect('多帶訂單頁面')
        return view_func(request, shop, intent, *args, **kwargs)
    return _wrapped_view