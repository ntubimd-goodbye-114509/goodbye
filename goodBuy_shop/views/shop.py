from django.db.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import *

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .utils import *
from .forms import *
from .time_f import *

# 商店
@login_required(login_url='login')
def addShop(request):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, '新增成功')
                return redirect('shop_list')
            except Exception as e:
                messages.error(request, f'新增失敗：{e}')
        else:
            messages.error(request, '表單驗證失敗')
    else:
        form = ShopForm(user=request.user)

    return render(request, 'shop_form.html', {'form': form})

@shop_owner_required
def deleteShop(request, shop):
    shop.delete()
    messages.success(request, '刪除成功！')
    return redirect('刪除成功導向')

# 多樣同時修改
@shop_owner_required
def edit_shop(request, shop):
    if request.method == 'POST':
        form = ShopForm(request.POST, request.FILES, instance=shop, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '修改成功')
            return redirect('shop_detail', shop_id=shop.id)
        else:
            messages.error(request, '修改失敗')
    else:
        form = ShopForm(instance=shop, user=request.user)

    return render(request, '商店修改', locals())

####################################################