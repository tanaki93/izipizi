from django.conf.urls import url
from projects_app import manager_views as views

urlpatterns = [
    url(r'^orders/$', views.manager_orders_view),
    url(r'^clients/$', views.manager_clients_view),
    url(r'^orders/([0-9]+)/$', views.manager_orders_item_view),
    url(r'^orders/product/([0-9]+)/$', views.manager_orders_product_item_view),

    url(r'^checking/product/$', views.manager_checking_product_view),
    url(r'^delivery/product/$', views.manager_checking_product_view),
    url(r'^checking/product/([0-9]+)/$', views.manager_checking_item_product_view),
    url(r'^packages/$', views.manager_packages_view),
    url(r'^packages/([0-9]+)/$', views.manager_packages_item_view),
    url(r'^packets/$', views.manager_packets_view),
    url(r'^packets/([0-9]+)/$', views.manager_packet_item_view),
]
