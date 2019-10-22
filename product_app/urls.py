from django.conf.urls import url, include
from product_app import views as product_views

urlpatterns = [
    url(r'^categories/$', product_views.categories_list_view),
]