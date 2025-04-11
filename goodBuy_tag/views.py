from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import *

def tag_search_api(request):
    q = request.GET.get('q', '')
    tags = Tag.objects.filter(name__icontains=q).values('name')[:10]
    return JsonResponse(list(tags), safe=False)