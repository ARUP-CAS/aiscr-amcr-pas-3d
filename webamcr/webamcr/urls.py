"""webamcr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from . import views
from documents.views import login, logout
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
	path('', views.home, name='home'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
	path('documents/', include('documents.urls')),
    path('pas/', include('detectors.urls')),
    path('django-rq/', include('django_rq.urls')),
    path('admin/', admin.site.urls),
    path('file/delete/<int:fileId>/', views.delete, name='delete_file'),
    path('user/', include('amcrusers.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

handler403 = 'webamcr.views.err_sid'

urlpatterns += staticfiles_urlpatterns()
