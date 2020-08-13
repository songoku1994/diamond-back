from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.template.context_processors import static
from django.urls import path, include, re_path

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('register', views.register),
                  path('myinfo', views.myinfo),
                  path('login', views.login),
                  path('Authentication', views.Authentication),
                  path('uploadNewArticle', views.uploadNewArticle),
                  path('judgeRepetitiveArticleName',views.judgeRepetitiveArticleName),
                  path('getAllArticle', views.getAllArticle),
                  path('getArticleContent/<int:id>', views.getArticleContent),
                  path('deleteArticle/<int:id>', views.deleteArticle),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
