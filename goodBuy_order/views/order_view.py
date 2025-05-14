from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from goodBuy_shop.models import *
from goodBuy_shop.views import shopInformation_many
from goodBuy_web.models import *
from ..models import *
from ..utils import *
from ..rush_utils import *
from utils import *
# -------------------------
# 訂單顯示 - 全部 - 分類+all
# -------------------------
@login_required(login_url='login')
def buyer_order_list(request):
    state = request.GET.get('state')
    shop = request.GET.get('shop')

    orders = Order.objects.filter(user=request.user)

    if shop:
        try:
            shop = Shop.objects.get(id=shop)
        except:
            messages.error(request, "商店不存在")
            return redirect('home')
        
        if shop.owner != request.user:
            messages.error(request, "無權查看此商店的訂單")
            return redirect('home')
        
        if shop.permission not in [1, 2]:
            messages.error(request, "商店不存在")
            return redirect('home')
        
        orders = orders.filter(shop=shop)

    if state:
        if state == '7':
            orders = orders.filter(order_state_id__in=[7, 8, 9, 10])
        else:
            orders = orders.filter(order_state_id=state)

    if state in ['7', '8', '9', '10']:
        title = '已取消'
    elif state:
        title = OrderState.objects.get(id=state).name
    else:
        title = '全部'

    return render(request, 'order_list.html', locals())
# -------------------------
# 訂單顯示 - 單一
# -------------------------
@login_required(login_url='login')
@order_exists_required
def order_detail(request, order):
    if order.user != request.user and order.shop.owner != request.user:
        messages.error(request, "無權查看此訂單")
        return redirect('home')

    product_orders = ProductOrder.objects.filter(order=order).select_related('product')

    if order.payment_category == 'remittance':
        payments = OrderPayment.objects.filter(order_id=order.id).order_by('-pay_time')
    else:
        payments = None

    deposit_amount = None
    tail_amount = None
    if order.payment_mode == 'split':
        deposit_ratio = order.shop.deposit_ratio or 50
        deposit_amount = order.total * deposit_ratio // 100
        tail_amount = (order.total - deposit_amount) + (order.second_supplement or 0)

    return render(request, 'order_detail.html', locals())
# -------------------------
# 待付款&付款記錄顯示 - 僅買家
# -------------------------
@login_required(login_url='login')
def my_payment_records(request):
    payments = OrderPayment.objects.filter(order__user=request.user)\
    .exclude(shop_payment__payment_id=1)\
    .select_related('order', 'shop_payment', 'order__shop')

    wait_confirmed = payments.filter(seller_state='wait confirmed')
    confirmed = payments.filter(seller_state='confirmed')
    returned = payments.filter(seller_state='returned')

    return render(request, 'payment_records.html',locals())
# -------------------------
# 多帶進行中 - 買家
# -------------------------
login_required(login_url='login')
def my_rush_shops(request):
    now = timezone.now()
    shop_ids = PurchaseIntent.objects.filter(
        user=request.user,
        shop__purchase_priority_id__in=[2, 3],
        shop__end_time__gt=now,
        shop__permission__id=1,
    ).values_list('shop_id', flat=True).distinct()

    shops = shopInformation_many(Shop.objects.filter(id__in=shop_ids))

    return render(request, 'my_rush_shops.html', {'shops': shops})
# -------------------------
# 多帶進行中 - 買家 - 單一
# -------------------------
@login_required(login_url='login')
@rush_exists_and_shop_exist_required
def my_rush_status_in_intent(request, shop, intent):
    now = timezone.now()
    remaining_seconds = (shop.end_time - now).total_seconds()

    intent_summaries = get_rush_summaries(shop, user=request.user)

    target_summary = None
    for summary in intent_summaries:
        if summary['user'] == request.user:
            target_summary = summary
            break

    if not target_summary:
        return redirect('some_error_page')

    product_list = target_summary['products']
    total_quantity = target_summary['total_quantity']
    total_price = target_summary['total_price']

    product_list.sort(key=lambda x: (not x['is_successful'], x['product'].id))

    return render(request, 'my_rush_status_in_shop.html', locals())

