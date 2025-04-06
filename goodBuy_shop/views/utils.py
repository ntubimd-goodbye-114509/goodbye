from django.shortcuts import redirect, get_object_or_404
from functools import wraps
from goodBuy_shop.models import Shop
from goodBuy_web.models import User
from goodBuy_tag.models import Tag

def user_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, user_id, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        return view_func(request, user_id=user.id, *args, **kwargs)
    return _wrapped_view

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

def shop_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, shop_id, *args, **kwargs):
        shop = get_object_or_404(Shop, id=shop_id)
        return view_func(request, shop_id, *args, **kwargs)
    return _wrapped_view

def tag_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, tag_id, *args, **kwargs):
        tag = get_object_or_404(Tag, id=tag_id)
        return view_func(request, tag_id, *args, **kwargs)
    return _wrapped_view