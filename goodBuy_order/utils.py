from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from goodBuy_shop.models import Product


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
