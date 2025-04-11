from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Want
from .forms import WantForm
from .utils import *

@login_required(login_url='login')
def create_want(request):
    if request.method == 'POST':
        form = WantForm(request.POST, request.FILES)
        if form.is_valid():
            want = form.save(commit=False)
            want.user = request.user
            want.save()
            return redirect('post_success')
        else:
            error = '請確認表單資料是否完整'
            return render(request, 'create_post.html', {'form': form, 'error': error})
    else:
        form = WantForm()
    return render(request, 'create_post.html', {'form': form})

@login_required(login_url='login')
@want_owner_required
def edit_want(request, want):
    if request.method == 'POST':
        form = WantForm(request.POST, request.FILES, instance=want)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=want.id)
        else:
            error = '請確認表單資料是否完整'
            return render(request, 'edit_post.html', {'form': form, 'post': post, 'error': error})
    else:
        form = WantForm(instance=want)
    return render(request, 'edit_post.html', locals())

@login_required(login_url='login')
@want_owner_required
def delete_want(request, want):
    if request.user == want.user:
        want.delete()
        messages.success(request, '刪除成功')
        return redirect('收物帖界面')
    return redirect('收物帖界面', want_id=want.id)
