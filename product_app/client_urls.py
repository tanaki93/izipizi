from django.conf.urls import url
from product_app import  views

urlpatterns = [
    url(r'^departments/$', views.client_departments_view),
]