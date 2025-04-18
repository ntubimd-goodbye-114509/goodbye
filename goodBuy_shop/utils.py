from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
from django.db.models import *
from django.contrib import messages
from django.shortcuts import *

from .models import *
from goodBuy_web.models import *
from goodBuy_tag.models import *
# =============跳轉頁面版本===============

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

        return view_func(request, shop, *args, **kwargs)
    return wrapper

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
        return view_func(request, shop, *args, **kwargs)
    return _wrapped_view

def product_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, product_id, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, '需要登入才可操作')
            return redirect('home')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, '找不到這個商品呢qwq')
            return redirect('home')

        if product.shop.owner.id != request.user.id:
            messages.error(request, '這不是您的商品哦')
            return redirect('home')

        return view_func(request, shop, *args, **kwargs)
    return _wrapped_view

def product_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, product_id, *args, **kwargs):
        try:
            product = Product.objects.get(id=product_id)
        except Shop.DoesNotExist:
            messages.error(request, '找不到這個商品呢qwq')
            return redirect('home')
        return view_func(request, shop, *args, **kwargs)
    return _wrapped_view

# =============json彈窗js版本===============
# from django.http import JsonResponse

# def login_required_json(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'error': '請先登入'}, status=401)
#         return view_func(request, *args, **kwargs)
#     return _wrapped_view

# def user_exists_required_json(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, user_id, *args, **kwargs):
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return JsonResponse({'error': '找不到使用者'}, status=404)
#         return view_func(request, user=user, *args, **kwargs)
#     return _wrapped_view

# def shop_owner_required_json(view_func):
#     @wraps(view_func)
#     def wrapper(request, shop_id, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'error': '請先登入'}, status=401)
#         try:
#             shop = Shop.objects.get(id=shop_id)
#         except Shop.DoesNotExist:
#             return JsonResponse({'error': '商店不存在'}, status=404)

#         if shop.owner != request.user:
#             return JsonResponse({'error': '您不是此商店的擁有者'}, status=403)

#         return view_func(request, shop=shop, *args, **kwargs)
#     return wrapper

# def shop_exists_required_json(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, shop_id, *args, **kwargs):
#         try:
#             shop = Shop.objects.get(id=shop_id)
#         except Shop.DoesNotExist:
#             return JsonResponse({'error': '商店不存在'}, status=404)
#         return view_func(request, shop_id=shop_id, shop=shop, *args, **kwargs)
#     return _wrapped_view

# def tag_exists_required_json(view_func):
#     @wraps(view_func)
#     def _wrapped_view(request, tag_id, *args, **kwargs):
#         try:
#             tag = Tag.objects.get(id=tag_id)
#         except Tag.DoesNotExist:
#             return JsonResponse({'error': '找不到這個標籤'}, status=404)
#         return view_func(request, tag=tag, *args, **kwargs)
#     return _wrapped_view
