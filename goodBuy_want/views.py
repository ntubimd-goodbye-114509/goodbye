from django.shortcuts import render, redirect
from .models import Preference
from django.contrib.auth.decorators import login_required

@login_required
def add_preference(request):
    if request.method == 'POST':
        name = request.POST.get('name')  # 從表單中抓取 name 欄位
        if name:
            Preference.objects.create(user=request.user, name=name)
            return redirect('preference_success')  # 導向成功頁
        else:
            error = "請填寫喜好名稱"
            return render(request, 'add_preference.html', {'error': error})
    
    return render(request, 'add_preference.html')

# Create your views here.
