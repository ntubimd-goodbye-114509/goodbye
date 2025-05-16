from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from goodBuy_shop.models import Permission
from ..models import *
from ..forms import *
from utils import *

# -------------------------
# 新增收物帖
# -------------------------
@login_required(login_url='login')
def add_want(request):
    form = WantForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            want = form.save(user=request.user)
            images = request.FILES.getlist('images')
            cover_index = int(request.POST.get('cover_index', -1))
            order_str = request.POST.get('image_order')

            if order_str:
                order_list = list(map(int, order_str.split(',')))
                sorted_images = [images[i] for i in order_list]
            else:
                sorted_images = images
            
            for idx, img in enumerate(sorted_images):
                WantImg.objects.create(want=want, img=img, is_cover=(idx == cover_index), position=idx)

            messages.success(request, '收物帖新增成功')
            return redirect('want_detail', want_id=want.id)
        else:
            messages.error(request, '表單資料有誤')
    return render(request, 'want_form.html', locals())
# -------------------------
# 編輯收物帖
# -------------------------
@login_required(login_url='login')
@want_owner_required
def edit_want(request, want):
    form = WantForm(request.POST or None, request.FILES or None, instance=want)
    if request.method == 'POST':
        if form.is_valid():
            want = form.save(user=request.user)
            images = request.FILES.getlist('images')
            cover_index = int(request.POST.get('cover_index', -1))
            order_str = request.POST.get('image_order')
            cover_image_id = request.POST.get('cover_image_id')
              # 處理既有圖片設為封面
            if cover_image_id:
                try:
                    _set_want_cover(want, cover_image_id)
                except Exception:
                    pass

            # 處理新上傳的圖片
            if order_str:
                order_list = list(map(int, order_str.split(',')))
                sorted_images = [images[i] for i in order_list]
            else:
                sorted_images = images

            for idx, img in enumerate(sorted_images):
                # 只有當沒有設定既有圖片為封面時，才讓新上傳的圖片可能成為封面
                is_cover = not cover_image_id and (idx == cover_index)
                WantImg.objects.create(want=want, img=img, is_cover=is_cover, position=idx)

            messages.success(request, '收物帖修改成功')
            return redirect('want_detail', want_id=want.id)
        else:
            messages.error(request, '表單資料有誤')
    return render(request, 'want_form.html', locals())
# -------------------------
# 刪除收物帖
# -------------------------
@login_required(login_url='login')
@want_owner_required
def delete_want(request, want):
    want.permission = Permission.objects.get(id=3)
    want.save()
    messages.success(request, '收物帖已刪除')
    return redirect('home')
# -------------------------
# 收物帖圖片刪除
# -------------------------
@login_required(login_url='login')
@want_owner_required
def delete_want_image(request, want, image_id):
    image = get_object_or_404(WantImg, id=image_id, want=want)
    image.delete()
    messages.success(request, '圖片已刪除')
    return redirect('edit_want', post_id=want.id)
# -------------------------
# 收物帖圖片設定封面 (內部幫助函數，不再暴露為URL路由)
# -------------------------
def _set_want_cover(want, image_id):
    """內部函數：設置收物帖封面圖片"""
    WantImg.objects.filter(want=want).update(is_cover=False)
    WantImg.objects.filter(id=image_id, want=want).update(is_cover=True)
