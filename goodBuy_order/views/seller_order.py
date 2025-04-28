from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required

from goodBuy_order.models import Order, OrderPayment
from goodBuy_shop.models import Shop
from ..utils import order_exists_and_shop_owner_required

# -------------------------
# 確認接收訂單
# -------------------------
@login_required(login_url='login')
@order_exists_and_shop_owner_required
def seller_confirm_order(request, shop, order):
    if order.order_state_id != 2:
        messages.error(request, "此訂單無法確認")
        return redirect('seller_order_manage', shop_id=shop.id)

    try:
        with transaction.atomic():
            order.order_state_id = 3
            order.save()

            # 建立 OrderPayment
            amount_to_pay = order.total
            deadline = timezone.now() + timezone.timedelta(days=7)

            OrderPayment.objects.create(
                order=order,
                amount=amount_to_pay,
                is_paid_by_user=False,
                seller_state='wait confirmed',
                deadline=deadline,
            )

            messages.success(request, f"已確認訂單，買家需於7天內完成付款")
            return redirect('seller_order_manage', shop_id=shop.id)

    except Exception as e:
        messages.error(request, f"訂單確認失敗：{e}")
        return redirect('seller_order_manage', shop_id=shop.id)
# -------------------------
# 出貨
# -------------------------  

# -------------------------
# 取消訂單
# -------------------------

# -------------------------
# 付款同意&不同意
# -------------------------