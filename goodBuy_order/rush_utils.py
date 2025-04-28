from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from goodBuy_shop.models import *
from goodBuy_web.models import *
from .models import *

# -------------------------
# 帶多邏輯判斷
# -------------------------
def get_rush_summaries(shop, user=None):
    intents = PurchaseIntent.objects.filter(shop=shop).prefetch_related('user', 'intent_products__product')

    intent_summaries = []
    for intent in intents:
        products = list(intent.intent_products.all())
        total_price = sum(ip.product.price * ip.quantity for ip in products)
        total_quantity = sum(ip.quantity for ip in products)

        product_list = []
        for ip in products:
            available = ip.product.stock
            if user:
                total_claimed = IntentProduct.objects.filter(product=ip.product)\
                    .exclude(intent__user=user)\
                    .aggregate(total=Sum('quantity'))['total'] or 0
                available = max(ip.product.stock - total_claimed, 0)

            product_list.append({
                'product': ip.product,
                'quantity': ip.quantity,
                'price': ip.product.price,
                'total_price': ip.product.price * ip.quantity,
                'available': available,
                'is_successful': ip.quantity <= available,
            })

        # 如果是自己的，就把 products 換成加上 is_successful
        if user and intent.user == user:
            products = product_list
            total_price = sum(p['total_price'] for p in product_list)
            total_quantity = sum(p['quantity'] for p in product_list)

        intent_summaries.append({
            'user': intent.user,
            'products': products,
            'total_price': total_price,
            'total_quantity': total_quantity,
            'intent_time': getattr(intent, 'created_at', timezone.now()),
        })

    # 排序
    if shop.purchase_priority_id == 2:
        intent_summaries.sort(key=lambda x: (-x['total_price'], x['intent_time']))
    else:
        intent_summaries.sort(key=lambda x: (-x['total_quantity'], x['intent_time']))

    return intent_summaries
# -------------------------
# 防尾刀，上限30分鐘
# -------------------------
def maybe_extend_rush(shop):
    now = timezone.now()
    remaining = (shop.end_time - now).total_seconds()

    if remaining <= 300:
        max_end_time = shop.start_time + timedelta(minutes=30)

        if shop.end_time + timedelta(minutes=5) <= max_end_time:
            shop.end_time += timedelta(minutes=5)
            shop.save()
        
    return shop
# -------------------------