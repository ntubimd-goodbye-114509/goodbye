from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Want

def want_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, post_id, *args, **kwargs):
        want = get_object_or_404(Want, id=post_id)

        if want.user != request.user:
            messages.error(request, '你不是這篇收物帖的主人喔')
            return redirect('home')

        return view_func(request, want, *args, **kwargs)
    return _wrapped_view
