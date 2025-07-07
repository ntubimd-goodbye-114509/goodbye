from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

from goodBuy_shop.models import Product,Shop
from goodBuy_order.models import *
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
