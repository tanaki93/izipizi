from django.conf.urls import url, include
from projects_app import views

urlpatterns = [
    url(r'^trendyol/brands/$', views.operator_brands_list_view),
    url(r'^trendyol/brands/([0-9]+)/$', views.operator_brands_item_view),
    url(r'^trendyol/brands/([0-9]+)/refresh/$', views.operator_brands_refresh_item_view),
    # url(r'^brands/([0-9]+)/departments/$', views.operator_departments_list_view),
    url(r'^trendyol/departments/([0-9]+)/$', views.operator_departments_item_view),
    url(r'^trendyol/categories/([0-9]+)/$', views.operator_categories_item_view),
    url(r'^izishop/departments/$', views.operator_departments_search_view),
    url(r'^izishop/departments/([0-9]+)/$', views.operator_department_item_view),
    url(r'^izishop/categories/$', views.operator_category_search_view),
    url(r'^documents/$', views.operator_documents_view),
    url(r'^documents/([0-9]+)/$', views.operator_documents_item_view),
    url(r'^documents/([0-9]+)/products/$', views.operator_documents_products_view),
    url(r'^documents/([0-9]+)/products/([0-9]+)/$', views.operator_documents_products_item_view),
    url(r'^izishop/categories/([0-9]+)/$', views.operator_category_item_view),
]