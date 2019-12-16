from django.conf.urls import url, include
from projects_app import views

urlpatterns = [
    url(r'^trendyol/brands/$', views.operator_brands_list_view),
    url(r'^trendyol/brands/([0-9]+)/$', views.operator_brands_item_view),
    # url(r'^trendyol/brands/([0-9]+)/refresh/$', views.operator_brands_refresh_item_view),
    # url(r'^brands/([0-9]+)/departments/$', views.operator_departments_list_view),
    url(r'^trendyol/departments/([0-9]+)/$', views.operator_departments_item_view),
    url(r'^trendyol/categories/([0-9]+)/$', views.operator_categories_item_view),

    url(r'^izishop/colours/$', views.operator_izishop_colours_view),
    url(r'^izishop/colours/([0-9]+)/$', views.operator_izishop_colours_item_view),
    url(r'^trendyol/colours/$', views.operator_colours_view),
    url(r'^trendyol/colours/([0-9]+)/$', views.operator_colours_item_view),


    url(r'^izishop/categories/$', views.operator_category_search_view),
    url(r'^trendyol/sizes/$', views.operator_sizes_view),
    url(r'^trendyol/sizes/([0-9]+)/$', views.operator_vend_size_item_view),
    url(r'^izishop/sizes/$', views.operator_izi_shop_sizes_view),
    url(r'^izishop/sizes/([0-9]+)/$', views.operator_izi_shop_sizes_item_view),
    url(r'^izishop/content/$', views.operator_izi_shop_content_view),
    url(r'^izishop/content/([0-9]+)/$', views.operator_izi_shop_content_item_view),
    url(r'^izishop/parent/categories/$', views.operator_parent_category_search_view),
    url(r'^documents/$', views.operator_documents_view),
    url(r'^documents/all/$', views.operator_documents_all_view),
    url(r'^documents/([0-9]+)/$', views.operator_documents_item_view),
    url(r'^documents/([0-9]+)/process/$', views.operator_documents_process_view),
    url(r'^documents/([0-9]+)/process/products/$', views.operator_documents_process_products_view),
    url(r'^documents/([0-9]+)/process/products/([0-9]+)/$', views.operator_documents_process_products_item_view),
    url(r'^documents/([0-9]+)/products/$', views.operator_documents_products_view),
    url(r'^documents/([0-9]+)/products/brands/$', views.operator_documents_products_brands_view),
    url(r'^documents/([0-9]+)/products/([0-9]+)/$', views.operator_documents_products_item_view),
    url(r'^izishop/parent/categories/([0-9]+)/$', views.operator_parent_category_item_view),
    url(r'^izishop/departments/$', views.operator_departments_search_view),
    url(r'^izishop/departments/([0-9]+)/$', views.operator_department_item_view),
    url(r'^izishop/departments/([0-9]+)/parents/$', views.operator_department_item_parents_view),
    url(r'^izishop/parents/([0-9]+)/$', views.operator_department_parents_item_view),
    url(r'^izishop/parents/([0-9]+)/categories/$', views.operator_department_parents_categories_view),
    url(r'^izishop/categories/([0-9]+)/$', views.operator_category_item_view),
    url(r'^vendor/products/$', views.operator_vendor_products_view),
]