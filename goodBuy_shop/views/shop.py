from django.db.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import *

from goodBuy_shop.models import *
from goodBuy_web.models import *
from ..utils import *
from ..forms import *
from .time_f import *

# 商店
@login_required(login_url='login')
def add_shop(request):
    form = ShopForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            shop = form.save()
            images = request.FILES.getlist('images')
            cover_index = int(request.POST.get('cover_index', -1))
            order_str = request.POST.get('image_order')

            if order_str:
                order_list = list(map(int, order_str.split(',')))
                sorted_images = [images[i] for i in order_list]
            else:
                sorted_images = images

            for idx, img in enumerate(sorted_images):
                ShopImg.objects.create(shop=shop, img=img, is_cover=(idx == cover_index), position=idx)

            messages.success(request, '商店新增成功')
            return redirect('shop_detail', shop_id=shop.id)
        else:
            messages.error(request, '表單資料有誤')
    return render(request, 'shop_form.html', {'form': form})

@login_required(login_url='login')
@shop_owner_required
def edit_shop(request, shop):
    form = ShopForm(request.POST or None, request.FILES or None, instance=shop, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            shop = form.save()
            images = request.FILES.getlist('images')
            cover_index = int(request.POST.get('cover_index', -1))
            order_str = request.POST.get('image_order')

            if order_str:
                order_list = list(map(int, order_str.split(',')))
                sorted_images = [images[i] for i in order_list]
            else:
                sorted_images = images

            for idx, img in enumerate(sorted_images):
                ShopImg.objects.create(shop=shop, img=img, is_cover=(idx == cover_index), position=idx)

            messages.success(request, '商店資訊修改成功')
            return redirect('shop_detail', shop_id=shop.id)
        else:
            messages.error(request, '表單資料有誤')
    return render(request, 'shop_form.html', {'form': form, 'shop': shop})

@login_required(login_url='login')
@shop_owner_required
def deleteShop(request, shop):
    shop.delete()
    messages.success(request, '刪除成功！')
    return redirect('刪除成功導向')

####################################################
# 圖片刪除
@login_required(login_url='login')
@shop_owner_required
def delete_shop_image(request, shop, image_id):
    image = get_object_or_404(ShopImg, id=image_id, shop=shop)
    image.delete()
    messages.success(request, '圖片已刪除')
    return redirect('shop_edit', shop_id=shop.id)

# 圖片設為封面
@login_required(login_url='login')
@shop_owner_required
def set_cover_image(request, shop, image_id):
    ShopImg.objects.filter(shop=shop).update(is_cover=False)
    ShopImg.objects.filter(id=image_id, shop=shop).update(is_cover=True)
    messages.success(request, '封面已更新')
    return redirect('shop_edit', shop_id=shop.id)
