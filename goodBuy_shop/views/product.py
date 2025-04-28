from django.db.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import *
from django.db import transaction

from goodBuy_shop.models import *
from goodBuy_web.models import *
from ..utils import *
from ..form.product_form import *

# -------------------------
# 新增product
# -------------------------
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
# -------------------------
# 修改product
# -------------------------
@login_required
@product_owner_required
def edit_product(request, product):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                with transaction.atomic():
                    product.is_delete = True
                    product.save()

                    # 2. 建立新商品
                    new_product = form.save(commit=False)
                    new_product.shop = product.shop

                    if not request.FILES.get('img'):
                        new_product.img = product.img

                    new_product.save()

                    messages.success(request, '修改成功')
                    return redirect('shop_detail', shop_id=new_product.shop.id)
            except Exception as e:
                messages.error(request, f'商品修改失敗：{e}')
    else:
        form = ProductForm(instance=product)

    return render(request, '商品form.html', locals())
# -------------------------
# 刪除product（軟刪除）
# -------------------------
@login_required
@product_owner_required
def delete_product(request, product):
    shop_id = product.shop.id
    product.is_delete = True
    product.save()
    messages.success(request, '商品已刪除')
    return redirect('商店頁面', shop_id=shop_id)
