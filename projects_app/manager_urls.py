from django.conf.urls import url
from projects_app import manager_views as views

urlpatterns = [
    url(r'^orders/$', views.manager_orders_view),
    url(r'^clients/$', views.manager_clients_view),
    url(r'^orders/([0-9]+)/$', views.manager_orders_item_view),
]
