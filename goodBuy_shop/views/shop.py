from goodBuy_shop.models import *
from .shop_f import *
from .utils import *
from django.db.models import *
from django.contrib.auth.decorators import login_required
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
    if not request.user.is_authenticated or request.user.id != user_id:
        shops = shops.filter(permission=Permission.objects.get(id=1))
        return render(request, '別人主頁賣場', locals())
    return render(request, '自己主頁賣場', locals())

def shopById_one(request, shop_id):
    if Shop.objects.filter(id=shop_id).exists():
        return render(request, '找不到賣場', msg='賣場被下架或不存在呢')
    shops = Shop.objects.get(id=shop_id)
    # 別人的
    if not request.user.is_authenticated or request.user.id != shops.owner.id:
        return render(request, '別人賣場', locals())
    return render(request, '自己賣場', locals())

def shopBySearch(request):
    kw = request.GET.get('keyWord')
    shops_by_name = Shop.objects.filter(name__icontains=kw)
    shops_by_tag = Shop.objects.filter(
            id__in=Shop_Tag.objects.filter(tag__name__icontains=kw).values_list('shop_id', flat=True)
        )
    shops = (shops_by_name | shops_by_tag).distinct()
    return render(request, '搜尋結果界面', locals())


####################################################
# 商店
@login_required(login_url='login')
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
        # payment等前端出寫法再修改
        payment_account_ids = request.POST.getlist('payment_ids')

        shop = Shop.objects.create(name=name, owner=request.user,introduce=introduce,img=img,start_time=start_time,
                            end_time=end_time,shop_state=Shop_State.objects.get(id=shop_state_id),
                            permission=Permission.objects.get(id=permission_id),purchase_priority=Purchase_Priority.objects.get(id=purchase_priority_id))
        
        for payment_account_id in payment_account_ids:
            Payment_Account.objects.create(shop=shop,payment=Payment_Account.objects.get(id=payment_account_id))
        
        return render(request, '新增成功導向', locals())
    return render(request, '新增表單')

@shop_owner_required
def deleteShop(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    shop.delete()
    return redirect('刪除成功導向')

# 多樣同時修改
@shop_owner_required
def editShop(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    payments = Shop_Payment.objects.select_related('Payment_Account').filter(shop=shop)
    if request.method == 'POST':
        name = request.POST.get('name')
        introduce = request.POST.get('introduce')
        img = request.FILES.get('img')
        start_time = timeFormatChange_now(request.POST.get('start_time'))
        end_time = timeFormatChange_longtime(request.POST.get('end_time'))
        shop_state_id = request.POST.get('shop_state')
        permission_id = request.POST.get('permission')
        # payment等前端出寫法再寫
        payment_account_ids = request.POST.getlist('payment_ids')
        old_payment_account_ids = [p.payment_account.id for p in payments]

        shop.name = name
        shop.introduce = introduce
        shop.img = img
        shop.start_time = start_time
        shop.end_time = end_time
        shop.shop_state = Shop_State.objects.get(id=shop_state_id)
        shop.permission = Permission.objects.get(id=permission_id)
        shop.save()
        
        # 有新出現的新增，沒出現的刪除
        to_add = set(payment_account_ids) - set(old_payment_account_ids)
        to_remove = set(old_payment_account_ids) - set(payment_account_ids)
        for pid in to_add:
            Shop_Payment.objects.create(
                shop=shop,
                payment_account=Payment_Account.objects.get(id=pid)
            )
        Shop_Payment.objects.filter(shop=shop, payment_account__id__in=to_remove).delete()
    return render(request, '修改成界面', locals())

####################################################
# 單項修改
@shop_owner_required
def change_shop_state(request, shop_id, shop_state_id):
    shop = Shop.objects.get(id=shop_id)
    shop.shop_state = Shop_State(id=shop_state_id)
    shop.save()
    return render(request, '')

@shop_owner_required
def change_permission(request, shop_id, permission_id):
    shop = Shop.objects.get(id=shop_id)
    shop.permission = Permission(id=permission_id)
    shop.save()
    return render(request, '')

@shop_owner_required
def change_start_time(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    start = timeFormatChange_now(request.GET.get('start_time'))
    shop.start_time = start
    shop.save()
    return render(request, '')

@shop_owner_required
def change_end_time(request, shop_id):
    shop = Shop.objects.get(id=shop_id)
    end = timeFormatChange_longtime(request.GET.get('end_time'))
    shop.start_time = end
    shop.save()
    return render(request, '')

####################################################