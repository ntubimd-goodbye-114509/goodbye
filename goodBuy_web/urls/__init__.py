from .web import urlpatterns as web_urlpatterns
from .user import urlpatterns as user_urlpatterns

urlpatterns = web_urlpatterns + user_urlpatterns,
