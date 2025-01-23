from django.contrib import admin
from .models import GroupClassification, Payment, State, Permission, Delivery, Group, User, Admin, OrderState, Order, Product, ProductOrder, Comment, Follow

# 注册模型到后台
admin.site.register(GroupClassification)
admin.site.register(Payment)
admin.site.register(State)
admin.site.register(Permission)
admin.site.register(Delivery)
admin.site.register(Group)
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(OrderState)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(ProductOrder)
admin.site.register(Comment)
admin.site.register(Follow)
