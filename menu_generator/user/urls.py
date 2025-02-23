from user.api.edit_user.urls import urlpatterns as edit_user_urls
from user.api.user.urls import urlpatterns as user_urls

urlpatterns = []

urlpatterns += user_urls
urlpatterns += edit_user_urls
