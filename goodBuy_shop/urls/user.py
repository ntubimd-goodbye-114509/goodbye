from django.urls import path
from goodBuy_shop.views import *

urlpatterns = [
    path('<int:shop_id>/collect/', shop_collect_toggle, name='shop_collect_toggle'),
    path('shop/collects/', my_shops_collected, name='my_shops_collected'),
]