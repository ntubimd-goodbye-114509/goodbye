from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from django.contrib import messages
from goodBuy_order.models import Order, Comment
from ..forms import CommentForm
from utils import *
# -------------------------
# 新增評論
# -------------------------
@login_required
@order_buyer_required
def create_comment(request, order_id):
    if Comment.objects.filter(user=request.user, order=order).exists():
        messages.warning(request, '您已對此訂單留下評論')
        return redirect('view_order_detail', order_id=order_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.order = order
            comment.save()
            messages.success(request, '評論新增成功')
            return redirect('view_order_detail', order_id=order_id)
    else:
        form = CommentForm()

    return render(request, 'comment/create_comment.html', locals())
# -------------------------
# 顯示賣家評論和平均評價
# -------------------------
@user_exists_and_not_blacklisted
def view_seller_comments(request, user):
    comments = Comment.objects.filter(order__shop__owner_id=user).select_related('user', 'order')

    average_rank = comments.aggregate(avg_rank=Avg('rank'))['avg_rank']

    return render(request, 'comment/seller_comment_list.html', locals())