from django.urls import path
from goodBuy_want.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('add/', add_want, name='add_want'),
    path('<int:want_id>/', wantById_one, name='want_detail'),
    path('<int:post_id>/edit/', edit_want, name='edit_want'),
    path('<int:post_id>/delete/', delete_want, name='delete_want'),
    path('<int:post_id>/delete_image/<int:image_id>/', delete_want_image, name='delete_want_image'),
    
    path('want/search/', wantBySearch, name='want_search'),
    path('want/search/user/<int:user_id>/', wantBySearch, name='want_search_by_user'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)