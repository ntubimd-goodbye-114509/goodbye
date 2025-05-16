from django.urls import path
from goodBuy_order.views import *

urlpatterns = [
    path('list/', buyer_order_list, name='buyer_order_list'),
    path('detail/<int:order_id>/', order_detail, name='order_detail'),
    path('payment_records/', my_payment_records, name='my_payment_records'),
    path('rush/shops/', my_rush_shops, name='my_rush_shops'),
    path('rush/<int:shop_id>/<int:intent_id>/', my_rush_status_in_intent, name='my_rush_status_in_intent'),
]