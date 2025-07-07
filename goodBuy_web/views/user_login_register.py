from django.shortcuts import *
from goodBuy_web.models import *
from django.contrib.auth import  authenticate,login,logout
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
            return render(request, 'common/register.html')
        
        elif User.objects.filter(email=email).exists():
            messages.error(request, '該電子郵件已被註冊')
            return render(request, 'common/register.html')
        
        elif password != password2:
            messages.error(request, '兩次輸入的密碼不相符')
            return render(request,'common/register.html')
        
        elif username == '':
            username = email.split('@')[0]

        elif User.objects.filter(username=username).exists():
            messages.error(request, '該用戶名已被使用')
            return render(request, 'common/register.html')    
            
        u = User.objects.create_user(username=username, password=password, email=email)
        u.save()
        return redirect('login')
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

        # 驗證當前密碼是否正確
        if not request.user.check_password(current_password):
            messages.error(request, '目前密碼不正確')
            return redirect('change_pass')  # 返回修改密碼頁面

        # 驗證新密碼與確認密碼是否一致
        if new_password != confirm_password:
            messages.error(request, '新密碼與確認密碼不一致')
            return redirect('change_pass')  # 返回修改密碼頁面
        
        # 更新密碼
        request.user.set_password(new_password)
        request.user.save()
        login(request, request.user)  

        messages.success(request, '密碼修改成功')
        return redirect('editprofile')  # 返回編輯個人資料頁面

    return render(request, 'common/change_pass.html')

    
@login_required
def editProfile(request):
    if request.method == 'POST':
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user) 

        # 更新電子郵件
        email = request.POST.get('email')
        if email and email != user.email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, '此電子郵件已被使用')
                return redirect('editprofile')
            user.email = email

        # 更新用戶名
        username = request.POST.get('username')
        if username and username != user.username:
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                messages.error(request, '此用戶名已被使用')
                return redirect('editprofile')
            user.username = username

        # 更新密碼
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password and confirm_password:
            if new_password != confirm_password:
                messages.error(request, '新密碼與確認密碼不一致')
                return redirect('editprofile')
            user.set_password(new_password)
            login(request, request.user)  

        # 更新暱稱
        nickname = request.POST.get('nickname')
        if nickname:
            profile.nickname = nickname

        # 更新自介
        bio = request.POST.get('bio')
        if bio:
            profile.bio = bio

        # 更新頭像
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        user.save()
        profile.save()
        messages.success(request, '個人資料已成功更新')
        return redirect('editprofile')

    return render(request, 'common/edit_profile.html')
