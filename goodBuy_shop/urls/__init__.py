from .shop import urlpatterns as shop_urlpatterns
from .shop_action import urlpatterns as action_urlpatterns
from .user import urlpatterns as user_urlpatterns

urlpatterns = (
    shop_urlpatterns +
    action_urlpatterns +
    user_urlpatterns
)
