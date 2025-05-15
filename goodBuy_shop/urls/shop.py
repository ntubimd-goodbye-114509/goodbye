from django.urls import path
from goodBuy_shop.views import *

urlpatterns = [
    path('add/', add_shop, name='add_shop'),
    # path('<int:shop_id>/add_product/', add_product_to_shop_view, name='add_shop_product'),
    path('<int:shop_id>/', shop_detail, name='shop_detail'),
    path('<int:shop_id>/edit/', shop_owner_required(edit_shop), name='shop_edit'),
    path('<int:shop_id>/delete/', deleteShop, name='shop_delete'),
]