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
    if request.method == 'POST':
        form = WantForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            want = form.save()
            images = request.FILES.getlist('images')
            cover_index = int(request.POST.get('cover_index') or -1)
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
    else:
        form = WantForm(user=request.user)

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
            want = form.save()
            images = request.FILES.getlist('images')
            cover_index_raw = request.POST.get('cover_index', '')
            cover_index = int(cover_index_raw) if cover_index_raw.isdigit() else -1
            order_str = request.POST.get('image_order')

            if order_str:
                order_list = list(map(int, order_str.split(',')))
                sorted_images = [images[i] for i in order_list]
            else:
                sorted_images = images

            for idx, img in enumerate(sorted_images):
                WantImg.objects.create(want=want, img=img, is_cover=(idx == cover_index), position=idx + want.images.count())

            messages.success(request, '收物帖修改成功')
            return redirect('want_detail', want_id=want.id)
        else:
            messages.error(request, '表單資料有誤')
    return render(request, 'want_form.html', {
    'form': form,
    'want': want,  
})
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
    return redirect('want_edit', want_id=want.id)
# -------------------------
# 收物帖圖片設定封面
# -------------------------
@login_required(login_url='login')
@want_owner_required
def set_cover_image(request, want, image_id):
    WantImg.objects.filter(want=want).update(is_cover=False)
    WantImg.objects.filter(id=image_id, want=want).update(is_cover=True)
    messages.success(request, '封面已更新')
    return redirect('want_edit', want_id=want.id)
