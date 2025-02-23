from .api.another.urls import urlpatterns as another_urls
from .api.auth.urls import urlpatterns as auth_urls
from .api.registration.urls import urlpatterns as registration_urls

urlpatterns = []

urlpatterns += auth_urls
urlpatterns += registration_urls
urlpatterns += another_urls
