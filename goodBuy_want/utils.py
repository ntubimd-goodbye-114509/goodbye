from django.shortcuts import redirect, get_object_or_404
from functools import wraps
from django.contrib import messages
from django.db.models import *
from django.contrib import messages
from django.shortcuts import *

from .models import *
from goodBuy_shop import Shop

from .utils import *
# -------------------------
# 收物帖擁有者檢查
# -------------------------
def want_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, post_id, *args, **kwargs):
        want = get_object_or_404(Want, id=post_id)

        if want.user != request.user:
            messages.error(request, '你不是這篇收物帖的主人喔')
            return redirect('home')

        return view_func(request, want, *args, **kwargs)
    return _wrapped_view
# -------------------------
# 收物帖存在檢查
# -------------------------
def want_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, want_id, *args, **kwargs):
        try:
            want = (
                Want.objects
                .select_related('permission', 'want_state', 'purchase_priority', 'owner')
                .prefetch_related(
                    Prefetch('want_tag_set', queryset=WantTag.objects.select_related('tag')),
                    Prefetch('images', queryset=WantImg.objects.all().order_by('-is_cover', 'position', 'update')),
                )
                .get(id=want_id)
            )
        except want.DoesNotExist:
            messages.error(request, '找不到這個收物帖呢qwq')
            return redirect('home')
        return view_func(request, want, *args, **kwargs)
    return _wrapped_view
# -------------------------
# 收物帖存在檢查
# -------------------------
def want_and_shop_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, want_id, shop_id, *args, **kwargs):
        try:
            want = Want.objects.prefetch_related(...).get(id=want_id)
            shop = Shop.objects.prefetch_related(...).get(id=shop_id)
        except Want.DoesNotExist:
            messages.error(request, '找不到這個收物帖')
            return redirect('home')
        except Shop.DoesNotExist:
            messages.error(request, '找不到這個商店')
            return redirect('home')

        return view_func(request, want, shop, *args, **kwargs)
    return _wrapped_view