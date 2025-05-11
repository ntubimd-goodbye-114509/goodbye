from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from collections import defaultdict
from itertools import chain
from datetime import datetime
from django.utils.timezone import localtime

from goodBuy_order.models import OrderPayment

@login_required
def payment_timeline(request):
    user = request.user

    income = OrderPayment.objects.filter(
        shop_payment__shop__owner=user
    ).annotate(direction_type='收入')

    expense = OrderPayment.objects.filter(
        order__buyer=user
    ).annotate(direction_type='支出')

    all_payments = sorted(
        chain(income, expense),
        key=lambda p: p.pay_time,
        reverse=True
    )

    grouped = defaultdict(list)
    for payment in all_payments:
        month_key = localtime(payment.pay_time).strftime('%Y-%m')
        grouped[month_key].append(payment)

    grouped = dict(sorted(grouped.items(), reverse=True))

    return render(request, 'orders/payment_timeline.html', {'grouped': grouped})
