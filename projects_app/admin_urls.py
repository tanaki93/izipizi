from django.conf.urls import url
from projects_app import admin_views as views

urlpatterns = [
    url(r'^document/brands/$', views.admin_brands_list_view),
    url(r'^document/users/$', views.admin_users_list_view),
    url(r'^document/statistics/$', views.admin_statistics_view),
    url(r'^document/list/$', views.admin_documents_view),
    url(r'^products/$', views.admin_products_view),
]