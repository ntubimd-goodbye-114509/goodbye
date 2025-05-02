from django.db.models import *
from django.contrib import messages
from django.shortcuts import *
from datetime import timezone

from ..models import *
from goodBuy_web.models import *
from utils import *
from ..shop_forms import *

# -------------------------
# 顯示商店公告
# -------------------------
@shop_exists_and_not_blacklisted
def showShopAnnouncement_many(request, shop):
    announcements = shop.shopAnnouncement_set.all().order_by('-update')
    return render(request, '顯示公告頁面', locals())

@announcement_exists_and_shop_visible
def showShopAnnouncement_one(request, shop, announcement_id):
    try:
        announcement = ShopAnnouncement.objects.get(id=announcement_id, shop=shop)
    except ShopAnnouncement.DoesNotExist:
        messages.error(request, '查無此公告')
        return redirect('shop_detail', shop_id=shop.id)
    return render(request, '顯示單一公告頁面', locals())
# -------------------------
# 新增商店公告
# -------------------------
@shop_owner_required
def addAnnouncement(request, shop):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            try:
                announcement = form.save(commit=False)
                announcement.shop = shop
                announcement.update = timezone.now()
                announcement.save()
                messages.success(request, '公告新增成功')
                return redirect('shop_list', shop_id=shop.id)
            except Exception as e:
                messages.error(request, f'公告新增失敗{e}')
        else:
            messages.error(request, '表單驗證失敗')
    else:
        form = AnnouncementForm()

    return render(request, 'announcement_form.html', locals())
# -------------------------
# 刪除商店公告
# -------------------------
@announcement_owner_required
def deleteAnnouncement(request, announcement):
    announcement.delete()
    messages.success(request, '公告刪除成功')
    return redirect('shop_detail', shop_id=announcement.shop.id)
# -------------------------
# 修改商店公告
# -------------------------
@announcement_owner_required
def editAnnouncement(request, announcement):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            try:
                announcement = form.save(commit=False)
                announcement.update = timezone.now()
                announcement.save()
                messages.success(request, '公告修改成功')
                return redirect('shop_detail', shop_id=announcement.shop.id)
            except Exception as e:
                messages.error(request, f'公告修改失敗：{e}')
        else:
            messages.error(request, '表單驗證失敗')
    else:
        form = AnnouncementForm(instance=announcement)

    return render(request, 'announcement_form.html', locals())
