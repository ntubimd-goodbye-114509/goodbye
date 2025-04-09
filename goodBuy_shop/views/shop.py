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
def add_or_edit_shop(request, shop_id=None):
    shop = get_object_or_404(Shop, id=shop_id) if shop_id else None

    if request.method == 'POST':
        form = ShopForm(request.POST, user=request.user, instance=shop)
        images = request.FILES.getlist('images')
        cover_index = int(request.POST.get('cover_index', -1))

        if form.is_valid():
            shop = form.save()

            if images and 0 <= cover_index < len(images):
                ShopImg.objects.filter(shop=shop, is_cover=True).update(is_cover=False)

            for idx, image_file in enumerate(images):
                ShopImg.objects.create(
                    shop=shop,
                    img=image_file,
                    is_cover=(idx == cover_index)
                )

            images_qs = ShopImg.objects.filter(shop=shop)

            if not images_qs.exists():
                ShopImg.objects.create(
                    shop=shop,
                    img='默認商店圖片',
                    is_cover=True
                )
            elif not images_qs.filter(is_cover=True).exists():
                first_img = images_qs.first()
                first_img.is_cover = True
                first_img.save()

            messages.success(request, '商店儲存成功')
            return redirect('shop_detail', shop_id=shop.id)

    else:
        form = ShopForm(user=request.user, instance=shop)

    return render(request, 'shop_form.html', {
        'shop_form': form,
        'shop': shop
    })

@shop_owner_required
def deleteShop(request, shop):
    shop.delete()
    messages.success(request, '刪除成功！')
    return redirect('刪除成功導向')

####################################################
# 圖片刪除
@login_required
@shop_owner_required
def delete_shop_image(request, shop, image_id):
    image = get_object_or_404(ShopImg, id=image_id, shop=shop)
    image.delete()
    messages.success(request, '圖片已刪除')
    return redirect('shop_edit', shop_id=shop.id)

# 圖片設為封面
@login_required
@shop_owner_required
def set_cover_image(request, shop, image_id):
    ShopImg.objects.filter(shop=shop).update(is_cover=False)
    ShopImg.objects.filter(id=image_id, shop=shop).update(is_cover=True)
    messages.success(request, '封面已更新')
    return redirect('shop_edit', shop_id=shop.id)
