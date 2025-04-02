from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Permission)
admin.site.register(Shop_State)
admin.site.register(Purchase_Priority)
admin.site.register(Payment)
admin.site.register(Shop)
admin.site.register(Shop_Payment)
admin.site.register(Shop_Tag)
admin.site.register(Product)

admin.site.register(Shop_Collect)
admin.site.register(Shop_Footprints)