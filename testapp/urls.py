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
                  path('judgeRepetitiveArticleName', views.judgeRepetitiveArticleName),
                  path('getAllArticle', views.getAllArticle),
                  path('getArticleContent/<int:id>', views.getArticleContent),
                  path('deleteArticle/<int:id>', views.deleteArticle),
                  path('getAbandonedArticle', views.getAbandonedArticle),
                  path('articleRecover/<int:id>', views.articleRecover),
                  path('changeUserInfo', views.changeUserInfo),
                  path('createTeam',views.createTeam),
                  path('completelyDeleteArticle/<int:id>', views.completelyDeleteArticle),
                  path('getListByKey',views.getListByKey),
                  path('inviteUserToTeam',views.inviteUserToTeam),
                  path('AcceptToJoinTeam',views.AcceptToJoinTeam),
                  path('myMessage',views.myMessage),
                  path('myTeam',views.myTeam),
                  path('getTeamMembers',views.getTeamMembers),
                  path('createComment',views.createComment),
                  path('createToComment',views.createToComment),
                  path('getTeamArticles',views.getTeamArticles),
                  path('getUserByKey',views.getUserByKey),
                  path('getCommentsOfArticle',views.getCommentsOfArticle),
                  path('exitTeam',views.exitTeam),
                  path('DisbandTeam',views.DisbandTeam),
                  path('getUserInfoByID',views.getUserInfoByID),
                  path('deleteBrowerHistory',views.deleteBrowerHistory),
                  path('deleteFavorite', views.deleteFavorite),
                  path('allFavorite', views.allFavorite),
                  path('addFavorite', views.addFavorite),
                  path('judgeFavorite', views.judgeFavorite),
                  path('getUserInfoByID',views.getUserInfoByID),
                  path('getBrowerHistory',views.getBrowerHistory),
                  path('check_mail', views.check_mail),
                  path('checkMessage',views.checkMessage),
                  path('judgeRepetitiveUserName', views.judgeRepetitiveUserName),
                  path('judgeRepetitiveEmail', views.judgeRepetitiveEmail),
                  path('deleteMessage',views.deleteMessage),
                  path('changePassword',views.changePassword),
                  path('changeTeamInfo',views.changeTeamInfo),
                  path('beginEdit',views.beginEdit),
                  path('endEdit',views.endEdit),
                  path('getTeamWorkTrend',views.getTeamWorkTrend),
                  path('changePasswordByEmail',views.changePasswordByEmail),
                  path('judgeIfEditing',views.judgeIfEditing),
                  path('uploadWorkTrend',views.uploadWorkTrend),
                  path('getMessagenum',views.getMessagenum),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
