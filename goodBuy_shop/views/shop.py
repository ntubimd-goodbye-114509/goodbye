from goodBuy_shop.models import *
from .shop_f import *
from django.db.models import *
from django.shortcuts import *
from django.core.files.storage import FileSystemStorage
from datetime import datetime


def shopAll_update(request):
    shops = Shop.objects.filter(permission=Permission.objects.get(id=1)).order_by('-date')
    return render(request, '主頁', locals())

####################################################
# user_id查詢
def shopByUserId_many(request, user_id):
    shops = Shop.objects.filter(id=user_id).order_by('-date')
    # 看別人的只顯示公開
    if request.user.id != user_id:
        shops = shops.filter(permission=Permission.objects.get(id=1))
        return render(request, '別人主頁賣場', locals())
    return render(request, '自己主頁賣場', locals())

def shopById_one(request, shop_id):
    if Shop.objects.filter(id=shop_id).exists():
        return render(request, '找不到賣場', msg='賣場被下架或不存在呢')
    shops = Shop.objects.get(id=shop_id)
    # 別人的
    if request.user.id != shops.owner.id:
        return render(request, '別人賣場', locals())
    return render(request, '自己賣場', locals())

def shopBySearch(request):
    kw = request.GET.get('keyWord')
    shops_by_name = Shop.objects.filter(name__icontains=kw)
    shops_by_tag = Shop.objects.filter(
            id__in=Shop_Tag.objects.filter(tag__name__icontains=kw).values_list('shop_id', flat=True)
        )
    shops = (shops_by_name | shops_by_tag).distinct()

####################################################
# 創建商店
def addShop(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        introduce = request.POST.get('introduce')
        img = request.FILES.get('img')
        start_time = timeFormatChange_now(request.POST.get('start_time'))
        end_time = timeFormatChange_longtime(request.POST.get('end_time'))
        shop_state_id = request.POST.get('shop_state')
        permission_id = request.POST.get('permission')
        purchase_priority_id = request.POST.get('purchase_priority')

        Shop.objects.create(name=name, owner=request.user,introduce=introduce,img=img,start_time=start_time,
                            end_time=end_time,shop_state=Shop_State.objects.get(id=shop_state_id),
                            permission=Permission.objects.get(id=permission_id),purchase_priority=Purchase_Priority.objects.get(id=purchase_priority_id))
        Shop.save()
        return render(request, '新增成功導向', locals())
    return render(request, '新增表單')

def deleteShop(request, shop_id):
    if Shop.objects.filter(id=shop_id).exists():
        return redirect('home')  
    shop = Shop.objects.get(id=shop_id)
    # 商店是否為當前使用者的，不是無法修改
    if shop.owner.id != request.user.id:
        return redirect('home')
    
    shop.delete()
    return redirect('刪除成功導向')

def editShop(request, shop_id):
    if Shop.objects.filter(id=shop_id).exists():
        return redirect('home')
    # 舊值，修改顯示
    shop = Shop.objects.get(id=shop_id)
    # 商店是否為當前使用者的，不是無法修改
    if shop.owner.id != request.user.id:
        return redirect('home')
    if request.method == 'POST':
        name = request.POST.get('name')
        introduce = request.POST.get('introduce')
        img = request.FILES.get('img')
        start_time = timeFormatChange_now(request.POST.get('start_time'))
        end_time = timeFormatChange_longtime(request.POST.get('end_time'))
        shop_state_id = request.POST.get('shop_state')
        permission_id = request.POST.get('permission')

        shop.name = name
        shop.introduce = introduce
        shop.img = img
        shop.start_time = start_time
        shop.end_time = end_time
        shop.shop_state = Shop_State.objects.get(id=shop_state_id)
        shop.permission = Permission.objects.get(id=permission_id)
        shop.save()

    return render(request, '修改成界面', locals())

# 待改
# def addShopPayment(request, shop_id):
#     if Shop.objects.filter(id=shop_id).exists():
#         return redirect('home')
#     shop = Shop.objects.get(id=shop_id)
#     if shop.owner.id != request.user.id:
#         return redirect('home')
#     if request.method == 'POST':
#         payment_id = request.POST.get('payment')
#         img = request.FILES.get('img')
#         account = request.POST.get('account')
#         Payment.objects.create(Payment=Payment.objects.get(id=payment_id), shop=shop_id,
#                             img=img, account=account)
#         Payment.save()
        