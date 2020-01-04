"""izi_back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from user_app import views as user_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/login/$', user_views.login_view),
    url(r'^api/v1/register/', user_views.auth_register),
    url(r'^api/v1/reauth/', user_views.reauth_view),
    url(r'^api/v1/post/([0-9]+)/', user_views.post),
    url(r'^api/v1/confirm/([-\w]+)/', user_views.confirm_user),
    url(r'^api/v1/resend/code/$', user_views.profile_resend_code_view),
    url(r'^api/v1/add_profile/$', user_views.add_profile_view),
    url(r'^api/v1/profile/([0-9]+)/$', user_views.edit_profile_view),
    url(r'^api/v1/profile/', include('user_app.urls')),
    url(r'^api/v1/product/', include('product_app.urls')),
    url(r'^api/v1/main/', include('product_app.client_urls')),
    url(r'^api/v1/manager/', include('projects_app.manager_urls')),
    url(r'^api/v1/project/', include('projects_app.urls')),
    url(r'^api/v1/operator/', include('projects_app.operator_urls')),
    url(r'^api/v1/admin/', include('projects_app.admin_urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)