#自訂塞選圖封面
from django import template
register = template.Library()

@register.filter
def get_cover(images):
    return images.filter(is_cover=True).first()