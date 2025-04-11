from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
from django.db.models import *
from django.contrib import messages
from django.shortcuts import *

from .models import *

def tag_exists_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, tag_id, *args, **kwargs):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            messages.error(request, '找不到這個Tag呢qwq')
            return redirect('home')
        return view_func(request, tag, *args, **kwargs)
    return _wrapped_view