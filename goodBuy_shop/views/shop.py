from goodBuy_shop.models import *
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
    shops = Shop.objects.filter(Q(name__icontains=kw)|
                                Q(introduce__icontains=kw)|
                                Q())

####################################################
# 創建商店
def addShop(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        introduce = request.POST.get('introduce')
        img = request.FILES.get('img')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        shop_state_id = request.POST.get('shop_state')
        permission_id = request.POST.get('permission')
        purchase_priority_id = request.POST.get('purchase_priority')
            
        if start_time:
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
        else:
            start_time = datetime.strptime(datetime.now(), "%Y-%m-%dT%H:%M")
        
        if end_time:
            end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
        else:
            end_time = datetime(9999, 12, 31, 23, 59, 59)

        Shop.objects.create(name=name, owner=request.user,introduce=introduce,img=img,start_time=start_time,
                            end_time=end_time,shop_state=Shop_State.objects.get(id=shop_state_id),
                            permission=Permission.objects.get(id=permission_id),purchase_priority=Purchase_Priority.objects.get(id=purchase_priority_id))
        Shop.save()
        return render(request, '', locals())
    return render(request, '')

def deleteShop(request, shop_id):
    if Shop.objects.filter(id=shop_id).exists():
        return redirect('主頁URL name')
    shop = Shop.objects.get(id=shop_id)
    shop.delete()
    return redirect('賣場管理頁面url name')