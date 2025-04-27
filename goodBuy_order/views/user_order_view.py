from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict
from django.utils import timezone
from django.db.models import F, Sum,Prefetch

from goodBuy_shop.models import *
from goodBuy_shop.views import shopInformation_many
from goodBuy_web.models import *
from ..models import *
from ..utils import *
# -------------------------
# 訂單顯示 - 使用者 - 全部 - 分類+all
# -------------------------
@login_required(login_url='login')
def buyer_order_list(request):
    state = request.GET.get('state')

    orders = Order.objects.filter(user=request.user)

    if state:
        if state == '7':
            orders = orders.filter(order_state_id__in=[7, 8, 9])
        else:
            orders = orders.filter(order_state_id=state)

    title = OrderState.objects.get(id=state).name if state else '全部' 

    return render(request, '買家訂單顯示', locals())
# -------------------------
# 訂單顯示 - 使用者 - 單一
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
# 待付款&付款記錄顯示 - 使用者
# -------------------------
@login_required(login_url='login')
def my_payment_records(request):
    payments = OrderPayment.objects.filter(order__user=request.user)\
    .exclude(shop_payment__payment_id=1)\
    .select_related('order', 'shop_payment', 'order__shop')

    wait_confirmed = payments.filter(seller_state='wait confirmed')
    confirmed = payments.filter(seller_state='confirmed')
    returned = payments.filter(seller_state='returned')

    return render(request, '付款界面',locals())
# -------------------------
# 多帶進行中 - 使用者
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
# 多帶進行中 - 使用者 - 單一
# -------------------------
@login_required(login_url='login')
@rush_exists_and_shop_exist_required
def my_rush_status_in_intent(request, shop, intent):
    now = timezone.now()
    remaining_seconds = (shop.end_time - now).total_seconds()
    
    products = intent.intent_products.select_related('product')

    product_list = []
    for ip in products:
        total_claimed = IntentProduct.objects.filter(
            product=ip.product
        ).exclude(intent__user=request.user).aggregate(total=Sum('quantity'))['total'] or 0

        available = max(ip.product.stock - total_claimed, 0)

        product_list.append({
            'product': ip.product,
            'quantity': ip.quantity,
            'price': ip.product.price,
            'total_price': ip.quantity * ip.product.price,
            'is_successful': ip.quantity <= available,
        })

    product_list.sort(key=lambda x: (not x['is_successful'], x['product'].id))

    total_quantity = sum(item['quantity'] for item in product_list)
    total_price = sum(item['total_price'] for item in product_list)

    return render(request, 'my_rush_status_in_shop.html', locals())
