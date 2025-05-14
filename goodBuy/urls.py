"""
URL configuration for goodBuy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from goodBuy_web.views.user_login_register import *  # Replace 'your_app' with the actual app name
from goodBuy_shop.views import *
from goodBuy_shop.views.product import add_product as add_product_to_shop_view
from goodBuy_order.views import *
from goodBuy_tag.views import *
from goodBuy_want.views import *
from goodBuy_web.views import *
from django.conf import settings
from django.conf.urls.static import static
from goodBuy_web.views import *

urlpatterns = [
    #共同頁面
    path('', homePage, name='home'),    #主頁
    path('admin/', admin.site.urls),
    path('login/', logins, name='login'),   #登入
    path('register/', register, name='register'), #註冊
    path('logout/', logouts, name='logout'),    #登出
    path('editprofile/', editprofile, name='editprofile'), #編輯個人資料

    #商店
    path('add_shop/', add_shop, name='add_shop'),
    path('shop/<int:shop_id>/', shop_owner_required(edit_shop), name='shop_detail'),
    #(特定商店)
    path('shop/<int:shop_id>/add_product/', add_product_to_shop_view, name='add_shop_product'),
    
    #訂單狀態更新
    path('order/<int:order_id>/buyer-action/', buyer_action, name='order_buyer_action'),
    path('order/<int:order_id>/seller-action/', seller_action, name='order_seller_action'),

    #付款方式
    path('payment/', payment_accounts, name='payment_accounts'),

    # 購物車
    path('cart/', view_cart, name='cart'),  # 購物車主畫面
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),  # 加入購物車
    path('cart/delete/<int:cart_item_id>/', delete_cart_item, name='delete_cart_item'),  # 刪除單項
    path('cart/delete_selected/', delete_multiple_cart_items, name='delete_multiple_cart_items'),  # 批次刪除
    path('cart/update_quantity/<int:cart_item_id>/', update_cart_quantity, name='update_cart_quantity'),  # 修改數量
    
    # 訂單
    path('orders/', buyer_order_list, name='buyer_order_list'),  # 所有訂單
    path('orders/<int:order_id>/', order_detail, name='order_detail'),  # 單一訂單詳情
    path('payments/', my_payment_records, name='my_payment_records'),  # 我的付款紀錄
    path('my_rush_shops/', my_rush_shops, name='my_rush_shops'),  # 多帶搶購頁面
    path('my_rush_status/<int:shop_id>/<int:intent_id>/', my_rush_status_in_intent, name='my_rush_status_in_intent'),  # 我的搶購結果
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)