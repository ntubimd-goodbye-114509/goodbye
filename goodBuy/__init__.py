import pymysql
pymysql.install_as_MySQLdb()


from .celery import app as celery_app
__all__ = ('celery_app',)

'''
定時自動創建order
# 啟動 Celery worker
celery -A goodBuy worker -l info

# 開另一個 terminal 啟動 beat
celery -A goodBuy beat -l info
'''