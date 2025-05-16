from django.urls import path
from goodBuy_order.views import *

urlpatterns = [
    path('<int:order_id>/', view_order_payment_history, name='view_payment_proofs'),
    path('list/', list_related_payments, name='list_related_payments'),
    path('second_supplement/<int:order_id>/', set_second_supplement, name='set_second_supplement'),
    
    path('audit/<int:payment_id>/', audit_payment, name='audit_payment'),
    path('notify/<int:order_id>/', notify_buyer_to_pay, name='notify_to_pay'),
]
