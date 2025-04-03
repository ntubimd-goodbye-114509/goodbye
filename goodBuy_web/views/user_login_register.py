from django.shortcuts import *
from django.contrib.auth import  authenticate,login,logout
from django.contrib.auth.hashers import check_password
import re
from django.contrib.auth.models import User
from django.contrib import messages

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