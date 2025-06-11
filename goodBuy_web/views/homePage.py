from django.shortcuts import render

from goodBuy_shop.shop_utils import *
from goodBuy_shop.models import *
from recommendation.weighting import *
from recommendation.hot_rank import get_hot_shops

def homePage(request):
    if request.user.is_authenticated:
        personalized = personalized_shop_recommendation(request.user, limit=10)
        hot = get_hot_shops(limit=10)
        hot = hot.exclude(id__in=[s.id for s in personalized])[:10]
        shops = list(personalized) + list(hot)
    else:
        shops = get_hot_shops(limit=20)
    
    shops = shopInformation_many(shops)
    return render(request, 'home.html', locals())