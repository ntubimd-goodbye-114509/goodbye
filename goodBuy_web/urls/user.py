from django.urls import path
from goodBuy_order.views import *

urlpatterns = [
    path('<int:user_id>/comments/', view_seller_comments, name='view_seller_comments'),
]