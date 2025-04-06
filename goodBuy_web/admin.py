from django.contrib import admin
from .models import *

# 注册模型到后台
admin.site.register(User)
admin.site.register(Blacklist)
admin.site.register(Payment)
admin.site.register(PaymentAccount)
