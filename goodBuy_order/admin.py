from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(PayState)
admin.site.register(OrderState)
admin.site.register(Order)
admin.site.register(ProductOrder)
admin.site.register(Cart)
admin.site.register(Comment)

