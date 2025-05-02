from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
from django.db.models import *

from .models import *
from goodBuy_web.models import *
from goodBuy_tag.models import *
# -------------------------
# 商店擁有者驗證
# -------------------------
def shop_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, shop_id, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, '需要登入才可操作')
            return redirect('home')
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            messages.error(request, '找不到這個商店呢qwq')
            return redirect('home')

        if shop.owner.id != request.user.id:
            messages.error(request, '這不是您的商店哦')
            return redirect('home')
        
        if shop.permission == 3:
            messages.error(request, '這個商店已經被刪除了')
            return redirect('home')

        return view_func(request, shop, *args, **kwargs)
    return wrapper
# -------------------------
# 商店存在驗證
# -------------------------
def shop_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, shop_id, *args, **kwargs):
        try:
            shop = (
                Shop.objects
                .select_related('permission', 'shop_state', 'purchase_priority', 'owner')
                .prefetch_related(
                    Prefetch('shop_payment_set', queryset=ShopPayment.objects.select_related('payment_account')),
                    Prefetch('shop_tag_set', queryset=ShopTag.objects.select_related('tag')),
                    Prefetch('images', queryset=ShopImg.objects.all().order_by('-is_cover', 'position', 'update')),
                )
                .get(id=shop_id)
            )
        except Shop.DoesNotExist:
            messages.error(request, '找不到這個商店呢qwq')
            return redirect('home')
        
        if shop.permission == 3:
            messages.error(request, '這個商店已經被刪除了')
            return redirect('home')

        if request.user.is_authenticated:
            is_blacklisted = Blacklist.objects.filter(user=shop.owner, black_user=request.user).exists()
            if is_blacklisted:
                messages.error(request, '你已被此賣家封鎖，無法查看。')
                return redirect('home')

        return view_func(request, shop, *args, **kwargs)

    return _wrapped_view
# -------------------------
# 商品擁有者驗證
# -------------------------
def product_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, product_id, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, '需要登入才可操作')
            return redirect('home')
        try:
            product = Product.objects.select_related('shop__owner').get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, '找不到這個商品呢qwq')
            return redirect('home')

        if product.shop.owner.id != request.user.id:
            messages.error(request, '這不是您的商品哦')
            return redirect('home')
        
        if product.is_delete:
            messages.error(request, '這個商品已經被刪除了')
            return redirect('home')

        return view_func(request, product, *args, **kwargs)
    return _wrapped_view
# -------------------------
# 商品存在驗證
# -------------------------
def product_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, product_id, *args, **kwargs):
        try:
            product = Product.objects.select_related('shop__owner').get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, '找不到這個商品呢qwq')
            return redirect('home')
        
        if product.shop.permission == 3:
            messages.error(request, '這個商店已經被刪除了')
            return redirect('home')
        
        if product.is_delete:
            messages.error(request, '這個商品已經被刪除了')
            return redirect('home')
        
        if request.user.is_authenticated:
            is_blacklisted = Blacklist.objects.filter(user=product.shop.owner, black_user=request.user).exists()
            if is_blacklisted:
                messages.error(request, '你已被此賣家封鎖，無法查看。')
                return redirect('home')
            
        return view_func(request, product, *args, **kwargs)
    return _wrapped_view
