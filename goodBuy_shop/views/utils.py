from django.shortcuts import redirect, get_object_or_404
from functools import wraps
from django.contrib import messages
from goodBuy_shop.models import Shop
from goodBuy_web.models import User
from goodBuy_tag.models import Tag

def user_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except:
            messages.error(request, "找不到使用者呢")
            return redirect('home')
        return view_func(request, user_id=user.id, *args, **kwargs)
    return _wrapped_view

def shop_owner_required(view_func):
    @wraps(view_func)
    def wrapper(request, shop_id, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, '需要登入才可操作')
            return redirect('home')
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            messages.error(request, '商店不存在或被消失了呢')
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
            shop = Shop.objects.get(id=shop_id)
        except Tag.DoesNotExist:
            messages.error(request, '找不到這個商店呢qwq')
            return redirect('home')
        return view_func(request, shop_id, *args, **kwargs)
    return _wrapped_view

def tag_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, tag_id, *args, **kwargs):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            messages.error(request, '找不到這個Tag呢qwq')
            return redirect('home')
        return view_func(request, tag_id, *args, **kwargs)
    return _wrapped_view