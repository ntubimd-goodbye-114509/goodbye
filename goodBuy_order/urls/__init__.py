from .order import urlpatterns as order_urlpatterns
from .order_action import urlpatterns as action_urlpatterns
from .payment import urlpatterns as payment_urlpatterns
from .cart import urlpatterns as cart_urlpatterns
from .comment import urlpatterns as comment_urlpatterns

urlpatterns = order_urlpatterns + action_urlpatterns + \
            payment_urlpatterns + cart_urlpatterns + \
            comment_urlpatterns
