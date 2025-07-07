from datetime import datetime
from django.utils import timezone
from django.utils.timezone import make_aware
from itertools import chain
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from goodBuy_order.models import OrderPayment

@login_required
def payment_timeline(request):
    user = request.user
    now = timezone.now()

    # 接收年份與月份（預設當年當月）
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))

    # 計算該月的起訖時間
    start_date = make_aware(datetime(year, month, 1))
    if month == 12:
        end_date = make_aware(datetime(year + 1, 1, 1))
    else:
        end_date = make_aware(datetime(year, month + 1, 1))

    # 收入與支出
    income = OrderPayment.objects.filter(
        shop_payment__shop__owner=user,
        pay_time__gte=start_date,
        pay_time__lt=end_date
    ).annotate(direction_type='收入')

    expense = OrderPayment.objects.filter(
        order__buyer=user,
        pay_time__gte=start_date,
        pay_time__lt=end_date
    ).annotate(direction_type='支出')

    all_payments = sorted(
        chain(income, expense),
        key=lambda p: p.pay_time,
        reverse=True
    )

    related_orders = {p.order.id: p.order for p in all_payments if p.order}

    for order in related_orders.values():
        order._product_orders = order.productorder_set.select_related('product__shop')

    for p in all_payments:
        if p.order and hasattr(p.order, '_product_orders'):
            p.products = p.order._product_orders
        else:
            p.products = []

    total_income = income.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expense.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'payment_timeline.html', {
        'year': year,
        'month': month,
        'all_payments': all_payments,
        'total_income': total_income,
        'total_expense': total_expense,
    })
