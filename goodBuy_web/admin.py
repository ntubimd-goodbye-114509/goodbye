from django.contrib import admin
from .models import User

# 注册模型到后台
admin.site.register(User)