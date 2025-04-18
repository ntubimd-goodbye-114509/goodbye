from django.db.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import *
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timezone

from goodBuy_shop.models import *
from goodBuy_web.models import *
from ..utils import *
from ..product_form import *

@login_required
@shop_owner_required
def add_product(request, shop):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, '商品新增成功')
            return redirect('商店頁面', shop_id=shop.id)
    else:
        form = ProductForm()
    return render(request, '商品form', locals())

@login_required
@product_owner_required
def edit_product(request, product):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, '商品修改成功')
            return redirect('商品form', locals())
    else:
        form = ProductForm(instance=product)
    return render(request, '商品form', locals())

@login_required
@product_owner_required
def delete_product(request, product):
    shop_id = product.shop.id
    product.delete()
    messages.success(request, '商品已刪除')
    return redirect('商店頁面', shop_id=shop_id)
