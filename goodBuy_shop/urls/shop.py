from django.urls import path
from goodBuy_shop.views import *
from django.conf.urls.static import static

urlpatterns = [
    path('add/', add_shop, name='add_shop'),
    # path('<int:shop_id>/add_product/', add_product_to_shop_view, name='add_shop_product'),
    path('<int:shop_id>/', shop_detail, name='shop_detail'),
    path('<int:shop_id>/edit/', edit_shop, name='shop_edit'),
    path('<int:shop_id>/delete/', deleteShop, name='shop_delete'),

    #搜尋
    path('shop/search/', shopBySearch, name='shop_search'),
    path('shop/search/user/<int:user_id>/', shopBySearch, name='shop_search_by_user'),

    #公告
    path('<int:shop_id>/announcement/add/', addAnnouncement, name='add_announcement'),
    path('announcement/<int:announcement_id>/edit/', editAnnouncement, name='edit_announcement'),
    path('announcement/<int:announcement_id>/delete/', deleteAnnouncement, name='delete_announcement'),

    #公告列表(單一及多筆)
    path('<int:shop_id>/announcements/', showShopAnnouncement_many, name='shop_announcement_list'),
    path('<int:shop_id>/announcement/<int:announcement_id>/', showShopAnnouncement_one, name='show_announcement'),

    # 圖片裁切
    path('crop/', shop_crop_view, name='shop_crop_view'),
    path('crop/delete/', delete_cropped_image, name='delete_cropped_image'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)