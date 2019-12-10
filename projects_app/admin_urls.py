from django.conf.urls import url
from projects_app import admin_views as views
from user_app import views as user_views


urlpatterns = [
    url(r'^document/brands/$', views.admin_brands_list_view),
    url(r'^document/users/$', views.admin_users_list_view),
    url(r'^document/users/([0-9]+)/$', user_views.edit_profile_view),
    url(r'^document/statistics/$', views.admin_statistics_view),
    url(r'^document/list/$', views.admin_documents_view),
    url(r'^documents/([0-9]+)/process/$', views.admin_documents_item_view),
    url(r'^documents/([0-9]+)/process/products/$', views.admin_documents_process_products_view),
    url(r'^products/$', views.admin_products_view),
    url(r'^countries/$', views.admin_countries_view),
    url(r'^currencies/$', views.admin_currencies_view),
    url(r'^currencies/([0-9]+)/$', views.admin_currencies_item_view),
    url(r'^languages/$', views.admin_languages_view),
    url(r'^languages/([0-9]+)/$', views.admin_languages_item_view),
    url(r'^exchanges/$', views.admin_exchanges_view),
    url(r'^exchanges/([0-9]+)/$', views.admin_exchanges_item_view),
    url(r'^countries/$', views.admin_countries_view),
    url(r'^countries/([0-9]+)/$', views.admin_countries_item_view),
]