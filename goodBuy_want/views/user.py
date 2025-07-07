from django.db.models import *
from django.contrib import messages
from django.shortcuts import *
from django.contrib.auth.decorators import login_required

from ..models import *
from goodBuy_web.models import *
from ..utils import *
from utils import *
from goodBuy_want.views.want_query import *
from goodBuy_shop.views.shop_query import shopInformation_many
# -------------------------
# 收物帖足跡
# -------------------------
@login_required(login_url='login')
def my_want_footprints(request):
    want_ids = WantFootprints.objects.filter(user=request.user).values_list('want_id', flat=True)
    wants = wantInformation_many(want.objects.filter(id__in=want_ids).order_by('-date'))
    return render(request, '足跡頁面', locals())
# -------------------------
# 選擇商店回復收物帖
# -------------------------
@login_required(login_url='login')
@want_exists_required
def choose_shop_to_reply(request, want):
    shops = shopInformation_many(Shop.objects.filter(owner=request.user, permission__id=1).order_by('-date'))
    
    replied_shop_ids = WantBack.objects.filter(user=request.user, want=want).values_list('shop_id', flat=True)

    return render(request, '收物帖界面+id', locals())
# -------------------------
# 收物帖回復
# -------------------------
@login_required(login_url='login')
@want_and_shop_exists_required()
def reply_want(request, want, shop):
    exists = WantBack.objects.filter(user=request.user, want=want, shop=shop).exists()
    if exists:
        messages.warning(request, f'你已經以「{shop.name}」回覆過這個收物帖了！')
    else:
        WantBack.objects.create(user=request.user, want=want, shop=shop)
        messages.success(request, f'你已成功以「{shop.name}」回覆該收物帖！')

    return redirect('want_detail', want_id=want.id)