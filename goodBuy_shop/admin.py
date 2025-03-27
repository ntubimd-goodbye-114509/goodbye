from django.contrib import admin
from .models import Tag,Permission,Shop_State,Purchase_Priority,Payment,Shop,Shop_Payment,Shop_Tag,Product
# Register your models here.

admin.site.register(Tag)
admin.site.register(Permission)
admin.site.register(Shop_State)
admin.site.register(Purchase_Priority)
admin.site.register(Payment)
admin.site.register(Shop)
admin.site.register(Shop_Payment)
admin.site.register(Shop_Tag)
admin.site.register(Product)