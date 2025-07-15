from django.shortcuts import render, get_object_or_404
from goodBuy_web.models import User  # 根據你的 User model 匯入

def view_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    return render(request, 'common/profile.html', {'profile_user': profile_user})
