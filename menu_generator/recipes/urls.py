from .api.filter.urls import urlpatterns as filter_urls
from .api.open_recipe.urls import urlpatterns as open_recipe_urls
from .api.user_recipe.urls import urlpatterns as user_recipe_urls

urlpatterns = []

urlpatterns += open_recipe_urls
urlpatterns += user_recipe_urls
urlpatterns += filter_urls
