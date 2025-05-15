from .want import urlpatterns as want_urlpatterns
from .want_action import urlpatterns as action_urlpatterns

urlpatterns = (
    want_urlpatterns +
    action_urlpatterns
)
