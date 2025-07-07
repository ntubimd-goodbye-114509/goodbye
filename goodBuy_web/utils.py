from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
from django.db.models import *
from django.shortcuts import *

from .models import *

def user_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "找不到使用者呢")
            return redirect('home')
        return view_func(request, user, *args, **kwargs)
    return _wrapped_view