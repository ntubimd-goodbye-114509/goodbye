from django.urls import path
from goodBuy_want.views import *

urlpatterns = [
    path('add/', add_want, name='add_want'),
    path('<int:want_id>/', wantById_one, name='want_detail'),
    path('<int:post_id>/edit/', edit_want, name='edit_want'),
    path('<int:post_id>/delete/', delete_want, name='delete_want'),
    path('<int:post_id>/delete_image/<int:image_id>/', delete_want_image, name='delete_want_image'),
]