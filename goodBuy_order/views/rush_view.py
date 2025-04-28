from django.shortcuts import render, redirect
from django.contrib import messages
from collections import defaultdict

from goodBuy_shop.models import *
from goodBuy_shop.utils import shop_exists_required
from goodBuy_web.models import *
from ..models import *
from ..utils import *
from ..rush_utils import *
# -------------------------
# 多帶商店顯示所有人多帶情況 - 流水表
# -------------------------
@shop_exists_required
@shop_exists_and_is_rush_required
def rush_status(request, shop):
    all_products = Product.objects.filter(shop=shop, is_delete=False)
    intent_summaries = get_rush_summaries(shop)

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
@shop_exists_and_is_rush_required
def rush_cross_table(request, shop):
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
