from django.conf.urls import url, include
from projects_app import views

urlpatterns = [
    url(r'^brands/$', views.brands_list_view),
    url(r'^categories/$', views.categories_list_view),
    url(r'^categories/zara/$', views.categories_zara_list_view),
    url(r'^links/trendyol/$', views.links_trendyol_list_view),
    url(r'^links/colour/$', views.links_colour_list_view),
]