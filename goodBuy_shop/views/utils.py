from django.shortcuts import redirect
from functools import wraps
from goodBuy_shop.models import Shop

def shop_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, shop_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            return redirect('home')

        if shop.owner.id != request.user.id:
            return redirect('home')

        return view_func(request, shop, *args, **kwargs)
    return wrapper
