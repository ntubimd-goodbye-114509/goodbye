from django.db.models import *
from django.contrib import messages
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
from datetime import timezone

from ..models import *
from goodBuy_web.models import *
from ..utils import *
from goodBuy_shop.views.shop_query import *
# -------------------------
# 標籤收藏
# -------------------------
@login_required(login_url='login')
@tag_exists_required
def tag_collect_toggle(request, tag):
    obj = TagCollect.objects.filter(user=request.user, tag=tag).first()
    if obj:
        obj.delete()
        messages.info(request, '已取消收藏')
    else:
        TagCollect.objects.create(user=request.user, tag=tag, date=timezone.now())
        messages.success(request, '收藏成功')

    return redirect('單tag界面', tag_id=tag.id)
# -------------------------
# 標籤收藏查看
# -------------------------
@login_required(login_url='login')
def my_tags_collected(request):
    tag_ids = TagCollect.objects.filter(user=request.user).values_list('tag_id', flat=True)

    shops = Tag.objects.filter(id__in=tag_ids).order_by('-date')
    return render(request, 'tag收藏瀏覽頁面', locals())