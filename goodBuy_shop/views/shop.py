import os
import uuid

from django.db.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import *
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings

from goodBuy_shop.models import *
from goodBuy_web.models import *
from utils import *
from ..shop_forms import *
from goodBuy_tag.models import Tag
from ..yolo_models.yolo_detect  import crop_detected_objects

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

# -------------------------
# 圖片自動切割
# -------------------------
import shutil
def clear_folder(folder_path):
    """安全刪除並重建資料夾（防錯、防權限）"""
    def handle_remove_readonly(func, path, exc):
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"[警告] 無法刪除 {folder_path}: {e}")
    os.makedirs(folder_path, exist_ok=True)

@login_required(login_url='login')
# @shop_owner_required
def shop_crop_view(request):
    # ✅ 使用者專屬子資料夾名稱
    user_folder = f"user_{request.user.id}"
    crop_folder = os.path.join(settings.MEDIA_ROOT, 'crop', user_folder)
    cropped_folder = os.path.join(settings.MEDIA_ROOT, 'cropped', user_folder)

    # ✅ 清空裁切資料夾並清除 session（只清除自己的）
    if request.GET.get('clear') == '1':
        clear_folder(crop_folder)
        clear_folder(cropped_folder)

        request.session.pop('uploaded_image', None)
        request.session.pop('cropped_images', None)

        return redirect('shop_crop_view')

    # ✅ 上傳圖片並裁切（只在 POST 執行一次）
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        # 🔥 上傳前先清空使用者資料夾（防止上一次殘留）
        clear_folder(crop_folder)
        clear_folder(cropped_folder)

        os.makedirs(crop_folder, exist_ok=True)
        os.makedirs(cropped_folder, exist_ok=True)

        # 儲存圖片到 crop/user_xx/
        ext = os.path.splitext(image.name)[1]
        filename = f"{uuid.uuid4().hex[:8]}{ext}"
        image_path = os.path.join(crop_folder, filename)

        with open(image_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        # 裁切處理，結果儲存在 cropped/user_xx/
        cropped_images = crop_detected_objects(image_path, cropped_folder)

        # 儲存相對路徑到 session（給前端使用）
        uploaded_image = os.path.join('crop', user_folder, filename).replace('\\', '/')
        cropped_images = [os.path.join('cropped', user_folder, os.path.basename(img)).replace('\\', '/') for img in cropped_images]

        request.session['uploaded_image'] = uploaded_image
        request.session['cropped_images'] = cropped_images

        return redirect('shop_crop_view')  # 重導向避免重複裁切

    # ✅ GET 請求：讀取 session 中結果
    uploaded_image = request.session.get('uploaded_image')
    cropped_images = request.session.get('cropped_images', [])

    return render(request, 'crop_result.html', {
        'uploaded_image': uploaded_image,
        'cropped_images': cropped_images
    })


# -------------------------
# 圖片自動切割 - 刪除不需要的
# -------------------------
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
@csrf_exempt
def delete_cropped_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        img_path = data.get('img')

        if not img_path:
            return JsonResponse({'error': '缺少圖片路徑'}, status=400)

        # 刪除實體檔案
        abs_path = os.path.join(settings.MEDIA_ROOT, img_path.replace('/', os.sep))
        if os.path.exists(abs_path):
            os.remove(abs_path)

        # 從 session 中移除
        cropped_images = request.session.get('cropped_images', [])
        if img_path in cropped_images:
            cropped_images.remove(img_path)
            request.session['cropped_images'] = cropped_images

        return JsonResponse({'success': True})

    return JsonResponse({'error': '只接受 POST'}, status=405)