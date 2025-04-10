from django.shortcuts import render, redirect
from .models import Preference
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

#增加
@login_required
def create_post(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        payment_method = request.POST.get('payment_method')
        product_image = request.FILES.get('product_image')

        if product_name and payment_method and product_image:
            Post.objects.create(
                user=request.user,
                product_name=product_name,
                payment_method=payment_method,
                product_image=product_image,
            )
            return redirect('post_success')
        else:
            error = '請完整填寫所有欄位'
            return render(request, 'create_post.html', {'error': error})

    return render(request, 'create_post.html')


#改
@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)


    if request.user != post.user:
        return redirect('post_detail', post_id=post.id)

    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        payment_method = request.POST.get('payment_method')
        product_image = request.FILES.get('product_image')

        if product_name and payment_method:
            post.product_name = product_name
            post.payment_method = payment_method

            if product_image:
                post.product_image = product_image

            post.save()
            return redirect('post_detail', post_id=post.id)
        else:
            error = '請填寫所有欄位'
            return render(request, 'edit_post.html', {'post': post, 'error': error})

    return render(request, 'edit_post.html', {'post': post})

#刪
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user == post.user:
        post.delete()
        return redirect('post_list') 

    return redirect('post_detail', post_id=post.id)

#留言
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')

    if request.method == 'POST':
        if request.user.is_authenticated:
            content = request.POST.get('content')
            if content:
                Comment.objects.create(post=post, user=request.user, content=content)
                return redirect('post_detail', post_id=post_id)
    
    return render(request, 'post_detail.html', {'post': post, 'comments': comments})

#刪留言
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)


    if request.user != comment.user:
        return HttpResponseForbidden("你沒有權限刪除這則留言")

    post_id = comment.post.id
    comment.delete()
    return redirect('post_detail', post_id=post_id)

#改留言
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        return HttpResponseForbidden("你沒有權限編輯這則留言")

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.save()
            return redirect('post_detail', post_id=comment.post.id)
        else:
            error = "留言不能為空白"
            return render(request, 'edit_comment.html', {'comment': comment, 'error': error})

    return render(request, 'edit_comment.html', {'comment': comment})





