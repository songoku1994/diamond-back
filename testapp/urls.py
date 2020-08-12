from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.template.context_processors import static
from django.urls import path, include, re_path

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('show_users', views.show_users),
                  path('register', views.register),
                  path('searchinfo/<int:id>', views.searchinfo),
                  path('login', views.login),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
