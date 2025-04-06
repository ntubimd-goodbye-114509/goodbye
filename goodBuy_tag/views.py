from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import *

# Create your views here.
def tag_search(request):
    q = request.GET.get('q', '')
    tags = Tag.objects.filter(name__icontains=q)
    results = [{'id': t.id, 'text': t.name} for t in tags]
    return JsonResponse({'results': results})