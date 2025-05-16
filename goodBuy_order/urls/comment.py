from django.urls import path
from goodBuy_order.views import *

urlpatterns = [
    path('order/<int:order_id>/comment/', create_comment, name='create_comment'),
    path('seller/<int:user_id>/comments/', view_seller_comments, name='view_seller_comments'),
]