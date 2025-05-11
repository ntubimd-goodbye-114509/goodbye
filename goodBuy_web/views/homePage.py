from django.shortcuts import render

from goodBuy_shop.shop_utils import *
from goodBuy_shop.models import *

def homePage(request):
    shops = shopInformation_many(Shop.objects.filter(permission__id=1).order_by('-update'))
    return render(request, 'home.html', locals())