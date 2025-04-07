from django.db.models import *
from django.contrib import messages
from django.shortcuts import *

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .utils import *
from .forms import *

####################################################
# 單項狀態修改
@shop_owner_required
def change_shop_state(request, shop, shop_state_id):
    try:
        shop.shop_state = ShopState.objects.get(id=shop_state_id)
        shop.save()
        messages.success(request, '商店狀態已更新')
    except ShopState.DoesNotExist:
        messages.error(request, '無效的狀態 ID')
    return redirect('商店界面', shop_id=shop.id)

@shop_owner_required
def change_permission(request, shop, permission_id):
    try:
        shop.permission = Permission.objects.get(id=permission_id)
        shop.save()
        messages.success(request, '權限已更新')
    except Permission.DoesNotExist:
        messages.error(request, '無效的權限 ID')
    return redirect('商店界面', shop_id=shop.id)

@shop_owner_required
def change_start_time(request, shop):
    start = timeFormatChange_now(request.GET.get('start_time'))
    if start:
        shop.start_time = start
        shop.save()
        messages.success(request, '開始時間已更新')
    else:
        messages.error(request, '時間格式錯誤')
    return redirect('商店界面', shop_id=shop.id)

@shop_owner_required
def change_end_time(request, shop):
    end = timeFormatChange_longtime(request.GET.get('end_time'))
    if end:
        shop.end_time = end
        shop.save()
        messages.success(request, '結束時間已更新')
    else:
        messages.error(request, '時間格式錯誤')
    return redirect('商店界面', shop_id=shop.id)


####################################################