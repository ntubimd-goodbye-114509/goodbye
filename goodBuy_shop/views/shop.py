from goodBuy_shop.models import *
from django.db.models import *
from django.shortcuts import *

def shopAll_update(request):
    shops = Shop.objects.filter(permission=Permission.objects.get(id=1)).order_by('-date')
    return render(request, '', locals())
# 使用者商店
# user_id查詢
def shopById_many(request, user_id):
    shops = Shop.objects.filter(id=user_id).order_by('-date')
    # 看別人的只顯示公開
    if request.user.id != user_id:
        shops = shops.filter(permission=Permission.objects.get(id=1))
        return render(request, '', locals())
    return render(request, '', locals())

def shopById_one(request, user_id):
    shops = Shop.objects.get(id=user_id)
    # 別人的
    if request.user.id != user_id:
        return render(request, '', locals())
    return render(request, '', locals())
