from django.db import models
from ..models import *
from django.core.exceptions import ValidationError
import re

def validate_tw_mobile(value):
    if not re.match(r'^09\d{8}$', value):
        raise ValidationError('請輸入有效的台灣手機號碼（格式為09xxxxxxxx）')
    
class UserAddress(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('Keelung City', '基隆市'),
        ('New Taipei City', '新北市'),
        ('Taipei City', '台北市'),
        ('Taoyuan City', '桃園市'),
        ('Hsinchu County', '新竹縣'),
        ('Hsinchu City', '新竹市'),
        ('Miaoli County', '苗栗縣'),
        ('Taichung City', '台中市'),
        ('Changhua County', '彰化縣'),
        ('Nantou County', '南投縣'),
        ('Yunlin County', '雲林縣'),
        ('Chiayi County', '嘉義縣'),
        ('Chiayi City', '嘉義市'),
        ('Tainan City', '台南市'),
        ('Kaohsiung City', '高雄市'),
        ('Pingtung County', '屏東縣'),
        ('Yilan County', '宜蘭縣'),
        ('Hualien County', '花蓮縣'),
        ('Taitung County', '台東縣'),
        ('Penghu County', '澎湖縣'),
        ('Kinmen County', '金門縣'),
        ('Lienchiang County', '連江縣'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10,validators=[validate_tw_mobile],verbose_name='手機號碼')
    city = models.CharField(max_length=100,choices=PAYMENT_MODE_CHOICES,default='')
    address = models.CharField(max_length=255)
