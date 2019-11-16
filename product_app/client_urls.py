from django.conf.urls import url
from product_app import  views

urlpatterns = [
    url(r'^departments/$', views.client_departments_view),
    url(r'^categories/$', views.client_categories_view),
    url(r'^categories/top/$', views.client_categories_top_view),
    url(r'^brands/$', views.client_brands_view),
    url(r'^sliders/$', views.client_sliders_view),
    url(r'^products/$', views.client_products_view),
]