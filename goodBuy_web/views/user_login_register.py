from django.shortcuts import *
from goodBuy_web.models import *
from django.contrib.auth import  authenticate,login,logout
from django.contrib.auth.hashers import check_password
import re
from django.contrib import messages
from django.contrib.auth.decorators import login_required

#登入
def logins(request):
    if request.user.is_active:
        return redirect('home')
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '帳號或密碼輸入錯誤')
    return render(request, 'common/login.html')

#註冊
def register(request):
    if request.user.is_active:
        return redirect('home')
    
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        password2=request.POST.get('password2')
        
        #驗證
        if email=='':
            messages.error(request, 'Email 不可為空')
            return render(request, 'register.html')
        
        elif User.objects.filter(email=email).exists():
            messages.error(request, '該電子郵件已被註冊')
            return render(request, 'register.html')
        
        elif password != password2:
            messages.error(request, '兩次輸入的密碼不相符')
            return render(request,'register.html')
        
        elif username == '':
            username = email.split('@')[0]

        elif User.objects.filter(username=username).exists():
            messages.error(request, '該用戶名已被使用')
            return render(request, 'register.html')    
            
        u = User.objects.create_user(username=username, password=password, email=email)
        u.save()
        return redirect('/login/')
    return render(request,'common/register.html')

#登出
def logouts(request):
    logout(request)
    return redirect('/')

#修改密碼
@login_required
def change_pass(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not check_password(current_password, request.user.password):
            messages.error(request, '目前密碼不正確')
        elif new_password != confirm_password:
            messages.error(request, '新密碼與確認密碼不一致')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, '密碼修改成功')
            return redirect('/login/')
    return render(request, 'common/change_pass.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # 更新電子郵件
        email = request.POST.get('email')
        if email and email != request.user.email:
            if User.objects.filter(email=email).exists():
                messages.error(request, '此電子郵件已被使用')
            else:
                request.user.email = email

        # 更新用戶名
        username = request.POST.get('username')
        if username and username != request.user.username:
            if User.objects.filter(username=username).exists():
                messages.error(request, '此用戶名已被使用')
            else:
                request.user.username = username

        # 更新密碼
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password and confirm_password:
            if new_password != confirm_password:
                messages.error(request, '新密碼與確認密碼不一致')
            else:
                request.user.set_password(new_password)

        # 更新個人介紹
        bio = request.POST.get('introduce')
        if bio:
            request.user.profile.bio = bio

        # 保存更改
        request.user.save()
        request.user.profile.save()
        messages.success(request, '個人資料已成功更新')
        return redirect('profile')