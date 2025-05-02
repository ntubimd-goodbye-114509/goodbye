# core/decorators_base.py
from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def object_exists_required(model, arg_name, context_name=None, not_found_msg='找不到資料', redirect_to='home'):
    """
    檢查物件是否存在並注入 context
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj_id = kwargs.get(arg_name)
            obj = get_object_or_404(model, id=obj_id)
            kwargs[context_name or model.__name__.lower()] = obj
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def object_owner_required(model, arg_name, owner_field, context_name=None, not_found_msg='找不到資料', owner_error_msg='您不是擁有者', redirect_to='home'):
    """
    檢查物件是否存在且為使用者擁有
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            obj_id = kwargs.get(arg_name)
            obj = get_object_or_404(model, id=obj_id)

            if not request.user.is_authenticated:
                messages.error(request, '需要登入才可操作')
                return redirect('home')

            # 支援 nested owner 欄位（例如 'shop.owner'）
            owner = obj
            for attr in owner_field.split('.'):
                owner = getattr(owner, attr)

            if owner != request.user:
                messages.error(request, owner_error_msg)
                return redirect(redirect_to)

            kwargs[context_name or model.__name__.lower()] = obj
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def blacklist_check(owner_getter, redirect_to='home', msg='你已被此使用者封鎖，無法查看。'):
    """
    檢查 request.user 是否被 owner 封鎖
    owner_getter: lambda obj: obj.owner or obj.shop.owner
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, obj, *args, **kwargs):
            if request.user.is_authenticated:
                owner = owner_getter(obj)
                from goodBuy_web.models import Blacklist
                if Blacklist.objects.filter(user=owner, black_user=request.user).exists():
                    messages.error(request, msg)
                    return redirect(redirect_to)
            return view_func(request, obj, *args, **kwargs)
        return _wrapped_view
    return decorator
