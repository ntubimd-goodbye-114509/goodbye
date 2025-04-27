from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict
from django.utils import timezone

from goodBuy_shop.models import *
from goodBuy_shop.utils import shop_exists_required
from goodBuy_web.models import *
from ..models import *
from ..utils import *
# -------------------------
# 多帶商店顯示所有人多帶情況 - 流水表
# -------------------------
@shop_exists_required
def rush_status(request, shop):
    if shop.purchase_priority_id not in [2, 3]:
        messages.error(request, "此商店不是搶購模式")
        return redirect('商店', shop_id=shop.id)

    if timezone.now() > shop.end_time and request.user != shop.owner:
        messages.info(request, '多帶已結算')
        return redirect('商店', shop_id=shop.id)

    all_products = Product.objects.filter(shop=shop, is_delete=False)

    intents = PurchaseIntent.objects.filter(shop=shop).prefetch_related('intent_products', 'user')

    intent_summaries = []
    for intent in intents:
        products = list(intent.intent_products.all())
        total_price = sum(ip.product.price * ip.quantity for ip in products)
        total_quantity = sum(ip.quantity for ip in products)

        intent_summaries.append({
            'user': intent.user,
            'products': products,
            'total_price': total_price,
            'total_quantity': total_quantity,
            'intent_time': getattr(intent, 'created_at', timezone.now()),
        })

    if shop.purchase_priority_id == 2:
        intent_summaries.sort(key=lambda x: (-x['total_price'], x['intent_time']))
    else:
        intent_summaries.sort(key=lambda x: (-x['total_quantity'], x['intent_time']))

    product_claimed = defaultdict(int)
    allocation_rows = []
    while True:
        row = {}
        all_empty = True

        for summary in intent_summaries:
            for ip in summary['products']:
                current_allocated = product_claimed[ip.product.id]
                available_stock = ip.product.stock
                if current_allocated < available_stock and ip.quantity > 0:
                    row[ip.product.id] = summary['user'].username
                    product_claimed[ip.product.id] += 1
                    ip.quantity -= 1
                    all_empty = False
                    break

        if all_empty:
            break
        allocation_rows.append(row)
            
    return render(request, 'user_rush_status.html', locals())
# -------------------------
# 多帶商店顯示所有人多帶情況 - 交叉表
# -------------------------
@shop_exists_required
def rush_cross_table(request, shop):
    if shop.purchase_priority_id not in [2, 3]:
        messages.error(request, "此商店非搶購模式")
        return redirect('home')

    if timezone.now() > shop.end_time and request.user != shop.owner:
        messages.info(request, '多帶已結算')
        return redirect('商店', shop_id=shop.id)
    
    intents = PurchaseIntent.objects.filter(shop=shop).prefetch_related('user', 'intent_products__product')

    user_summary = defaultdict(lambda: {
        'total_quantity': 0,
        'total_price': 0,
    })

    for intent in intents:
        for ip in intent.intent_products.all():
            user_summary[intent.user]['total_quantity'] += ip.quantity
            user_summary[intent.user]['total_price'] += ip.product.price * ip.quantity

    cross_table = []
    for user, summary in user_summary.items():
        cross_table.append({
            'user': user,
            'total_quantity': summary['total_quantity'],
            'total_price': summary['total_price'],
        })

    if shop.purchase_priority_id == 2:
        cross_table.sort(key=lambda x: (-x['total_price']))
    else:
        cross_table.sort(key=lambda x: (-x['total_quantity']))

    return render(request, 'rush_cross_simple.html', locals())