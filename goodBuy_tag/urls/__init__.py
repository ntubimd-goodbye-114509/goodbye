from .tag import urlpatterns as tag_urlpatterns
from .user import urlpatterns as user_urlpatterns

urlpatterns = tag_urlpatterns + user_urlpatterns
