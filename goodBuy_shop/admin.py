from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Permission)
admin.site.register(ShopState)
admin.site.register(PurchasePriority)
admin.site.register(Shop)
admin.site.register(ShopPayment)
admin.site.register(ShopTag)
admin.site.register(Product)

admin.site.register(ShopCollect)
admin.site.register(ShopFootprints)