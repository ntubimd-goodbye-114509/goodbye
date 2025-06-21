from django.shortcuts import render

from goodBuy_shop.shop_utils import *
from goodBuy_shop.weighting import *
from goodBuy_shop.hot_rank import *

from goodBuy_want.want_utils import *
from goodBuy_want.weighting import *
from goodBuy_want.hot_rank import *

def homePage(request):
    if request.user.is_authenticated:
        personalized = personalized_shop_recommendation(request.user, limit=10)
        hot_shop = get_hot_shops(limit=10)
        hot_shop = hot_shop.exclude(id__in=[s.id for s in personalized])[:10]
        shops = list(personalized) + list(hot_shop)

        personalized = personalized_want_recommendation(request.user, limit=10)
        hot_want = get_hot_wants(limit=10)
        hot_want = hot_want.exclude(id__in=[w.id for w in personalized])[:10]
        wants = list(personalized) + list(hot_want)
    else:
        shops = get_hot_shops(limit=20)
        wants = get_hot_wants(limit=20)
    
    shops = shopInformation_many(shops)
    wants = wantInformation_many(wants)

    return render(request, 'home.html', locals())