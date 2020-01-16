from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^google/$', views.GoogleLogin.as_view(), name='google_login'),
    url(r'^facebook/$', views.FacebookLogin.as_view(), name='facebook_login')
]
