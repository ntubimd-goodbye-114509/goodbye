# goodBuy_order/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def auto_settle_rush_orders():
    call_command('settle_rush_orders')  # 這是你寫的 management command 名稱
