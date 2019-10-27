from django.conf.urls import url, include
from projects_app import views

urlpatterns = [
    url(r'^brands/$', views.brands_list_view),
]