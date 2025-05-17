from django.db.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import *
from django.utils import timezone
from django.http import JsonResponse

from goodBuy_shop.models import *
from goodBuy_web.models import *
from utils import *
from ..shop_forms import *
from goodBuy_tag.models import Tag

# -------------------------
# 新增商店
# -------------------------
@login_required(login_url='login')
def add_shop(request):
    form = ShopForm(request.POST or None, request.FILES or None, user=request.user)
    if request.method == 'POST':
        if form.is_valid():
            shop = form.save()

            # 封面圖片處理
            print("上傳圖片檔案們：", request.FILES.getlist('images'))
            images = request.FILES.getlist('images')
            cover_index_str = request.POST.get('cover_index')
            try:
                cover_index = int(cover_index_str)
            except (TypeError, ValueError):
                cover_index = -1
            order_str = request.POST.get('image_order')
            if order_str:
                order_list = list(map(int, order_str.split(',')))
                sorted_images = [images[i] for i in order_list if i < len(images)]
            else:
                sorted_images = images

            for idx, img in enumerate(sorted_images):
                ShopImg.objects.create(shop=shop, img=img, is_cover=(idx == cover_index), position=idx)

            # 商品處理
            names = request.POST.getlist('product_name[]')
            prices = request.POST.getlist('product_price[]')
            qtys = request.POST.getlist('product_qty[]')
            product_images = request.FILES.getlist('product_image')

            success_count = 0
            for i in range(len(names)):
                try:
                    if not names[i] or not prices[i] or not qtys[i]:
                        continue  # 跳過空白欄位
                    Product.objects.create(
                        shop=shop,
                        name=names[i],
                        price=prices[i],
                        stock=qtys[i],
                        amount=qtys[i],
                        img=product_images[i] if i < len(product_images) else None
                    )
                    success_count += 1
                except Exception as e:
                    print(f"商品新增失敗（第 {i+1} 筆）：{e}")

            messages.success(request, f'商店已建立，{success_count} 個商品成功新增。')
            return redirect('shop_detail', shop_id=shop.id)
        else:
            print('表單驗證失敗:', form.errors)
            messages.error(request, '表單資料有誤')
    return render(request, 'add_shop.html', {'form': form})
# -------------------------
# 修改商店資訊（多個）
# -------------------------
@login_required(login_url='login')
@shop_owner_required
def edit_shop(request, shop):
    form = ShopForm(request.POST or None, request.FILES or None, instance=shop, user=request.user)

    if request.method == 'POST':
        if form.is_valid():
            shop = form.save(commit=False)
            shop.update = timezone.now()
            shop.save()

            # 封面圖片處理（只有有上傳才刪掉重建）
            images = request.FILES.getlist('images')
            if images:
                shop.images.all().delete()

                cover_index_raw = request.POST.get('cover_index')
                cover_index = int(cover_index_raw) if cover_index_raw and cover_index_raw.isdigit() else -1
                order_str = request.POST.get('image_order')
                if order_str:
                    order_list = list(map(int, order_str.split(',')))
                    sorted_images = [images[i] for i in order_list if i < len(images)]
                else:
                    sorted_images = images

                for idx, img in enumerate(sorted_images):
                    ShopImg.objects.create(
                        shop=shop,
                        img=img,
                        is_cover=(idx == cover_index),
                        position=idx
                    )

            # 商品處理
            names = request.POST.getlist('product_name[]')
            prices = request.POST.getlist('product_price[]')
            qtys = request.POST.getlist('product_qty[]')
            product_images = request.FILES.getlist('product_image')

            old_products = list(shop.product_set.filter(is_delete=False))
            shop.product_set.filter(is_delete=False).update(is_delete=True)

            for i in range(len(names)):
                try:
                    if not names[i] or not prices[i] or not qtys[i]:
                        continue

                    product = Product(
                        shop=shop,
                        name=names[i],
                        price=prices[i],
                        stock=qtys[i],
                        amount=qtys[i],
                    )

                    if i < len(product_images) and product_images[i]:
                        product.img = product_images[i]
                    elif i < len(old_products):
                        product.img = old_products[i].img

                    product.save()
                except Exception as e:
                    print(f"商品第 {i+1} 筆新增失敗：{e}")

            messages.success(request, '商店資訊修改成功')
            return redirect('shop_detail', shop_id=shop.id)
        else:
            messages.error(request, '表單資料有誤')

    return render(request, 'edit_shop.html', {
        'form': form,
        'shop': shop,
        'predefined_tags': Tag.objects.values_list('name', flat=True),
        'selected_tags': shop.shoptag_set.values_list('tag__name', flat=True),
        'products': shop.product_set.filter(is_delete=False),
        'shop_images': shop.images.all(),
    })
@shop_owner_required
def shop_detail(request, shop):
    return render(request, 'shop_detail.html', {
        'shop': shop,
        'products': shop.product_set.filter(is_delete=False),
        'shop_images': shop.images.all(),
        'predefined_tags': Tag.objects.values_list('name', flat=True),
        'selected_tags': shop.shoptag_set.values_list('tag__name', flat=True),
    })

# @login_required(login_url='login')
# def edit_shop(request, shop):
#     form = ShopForm(request.POST or None, request.FILES or None, instance=shop, user=request.user)
    
#     if request.method == 'POST':
#         if form.is_valid():
#             shop = form.save(commit=False)
#             shop.update = timezone.now()
#             shop.save()

#             shop.images.all().delete()

#             images = request.FILES.getlist('images')
#             cover_index_raw = request.POST.get('cover_index')
#             cover_index = int(cover_index_raw) if cover_index_raw and cover_index_raw.isdigit() else -1
#             order_str = request.POST.get('image_order')

#             if order_str and images:
#                 order_list = list(map(int, order_str.split(',')))
#                 sorted_images = [images[i] for i in order_list if i < len(images)]
#             else:
#                 sorted_images = images

#             for idx, img in enumerate(sorted_images):
#                 ShopImg.objects.create(
#                     shop=shop,
#                     img=img,
#                     is_cover=(cover_index != -1 and idx == cover_index),
#                     position=idx
#                 )

#             messages.success(request, '商店資訊修改成功')
#             return redirect('shop_detail', shop_id=shop.id)
#         else:
#             messages.error(request, '表單資料有誤')

#     return render(request, 'shop_detail.html', {
#     'form': form,
#     'shop': shop,
#     'predefined_tags': Tag.objects.values_list('name', flat=True),
#     'selected_tags': shop.shoptag_set.values_list('tag__name', flat=True),
#     'products': shop.product_set.filter(is_delete=False),
#     'shop_images': shop.images.all(),
# })

# -------------------------
# 刪除商店（軟刪除）
# -------------------------
@login_required(login_url='login')
@shop_owner_required
def deleteShop(request, shop):
    has_unfinished_orders = Order.objects.filter(shop=shop, order_state__in=[1,2,3,4,5]).exists()

    if has_unfinished_orders:
        messages.error(request, '賣場有未完成訂單，無法刪除。請先當前訂單。')
        return redirect('shop_detail', shop_id=shop.id)

    shop.permission = Permission.objects.get(id=3)
    shop.save()
    messages.success(request, '賣場已刪除')
    return redirect('home')
# -------------------------
# 商店刪除圖片
# -------------------------
@login_required(login_url='login')
@shop_owner_required
def delete_shop_image(request, shop, image_id):
    image = get_object_or_404(ShopImg, id=image_id, shop=shop)
    image.delete()
    messages.success(request, '圖片已刪除')
    return redirect('shop_edit', shop_id=shop.id)
# -------------------------
# 重新設定封面
# -------------------------
@login_required(login_url='login')
@shop_owner_required
def set_cover_image(request, shop, image_id):
    ShopImg.objects.filter(shop=shop).update(is_cover=False)
    ShopImg.objects.filter(id=image_id, shop=shop).update(is_cover=True)
    messages.success(request, '封面已更新')
    return redirect('shop_edit', shop_id=shop.id)
