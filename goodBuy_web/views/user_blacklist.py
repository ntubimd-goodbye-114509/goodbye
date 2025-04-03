from goodBuy_web.models import Blacklist
from django.shortcuts import *
from django.contrib.auth.decorators import login_required
import re
from django.contrib import messages


@login_required
def view_blacklist(request):
    blacklist = Blacklist.objects.filter(user=request.user)
    return render(request, 'blacklist.html', {'blacklist': blacklist})

@login_required
def add_to_blacklist(request):
    if request.method == 'POST':
        blocked_user_id = request.POST.get('blocked_user_id')
        if Blacklist.objects.filter(user=request.user, blocked_user_id=blocked_user_id).exists():
            messages.error(request, '該用戶已存在於您的黑名單中')
        else:
            Blacklist.objects.create(user=request.user, blocked_user_id=blocked_user_id)
            messages.success(request, '成功加入黑名單')
        return redirect('view_blacklist')

@login_required
def remove_from_blacklist(request):
    if request.method == 'POST':
        blocked_user_id = request.POST.get('blocked_user_id')
        Blacklist.objects.filter(user=request.user, blocked_user_id=blocked_user_id).delete()
        messages.success(request, '已從黑名單中移除')
        return redirect('view_blacklist')