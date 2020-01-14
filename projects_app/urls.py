from django.conf.urls import url, include
from projects_app import views

urlpatterns = [
    url(r'^brands/$', views.brands_list_view),
    url(r'^categories/$', views.categories_list_view),
    url(r'^brands/zara/$', views.zara_item_view),
    url(r'^brands/handm/$', views.handm_item_view),
    url(r'^links/$', views.links_brand_list_view),
    url(r'^update/links/$', views.links_update_list_view),
]