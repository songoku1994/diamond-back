from django.core import serializers
import json
from django.http import HttpResponse, JsonResponse, FileResponse, Http404, StreamingHttpResponse
from .models import User, UserToken, Article, MemberShip, Team
import uuid
from testapp import models
from datetime import datetime
# Create your views here.
from django.views.decorators.http import require_http_methods


def object_to_json(obj):
    return dict([(kk, obj.__dict__[kk]) for kk in obj.__dict__.keys() if kk != "_state"])


@require_http_methods(["POST"])
def register(request):  # 注册
    print(request)
    response = {}
    try:
        name = request.POST.get('name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(name=name):
            response['msg'] = "repetitive username"
            response['error_num'] = 1
            response['state'] = 0
        elif User.objects.filter(email=email):
            response['msg'] = "repetitive email"
            response['error_num'] = 2
            response['state'] = 0
        else:
            p = User()
            p.name = name
            p.password = password
            p.email = email
            p.save()
            response['msg'] = "success"
            response['state'] = 1
    except Exception as e:
        response['msg'] = str(e)
        response['error_num'] = -1
        response['state'] = 0
    return JsonResponse(response)


@require_http_methods(["GET"])
def login(request):  # 登录
    response = {}
    try:
        name = request.GET['name']
        password = request.GET['password']
        if User.objects.filter(name=name):
            user = User.objects.get(name=name)
            if user.password == password:
                token = uuid.uuid4()
                models.UserToken.objects.update_or_create(user=user, defaults={'token': token})
                response['msg'] = "login successfully!"
                response['state'] = 1
                response['name'] = name
                response['token'] = token
            else:
                response['msg'] = "Wrong username or password,try again!"
                response['state'] = 2
        else:
            response['msg'] = "Wrong username or password,try again!"
            response['state'] = 3
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 4

    return JsonResponse(response)


@require_http_methods(["GET"])
def myinfo(request):  # 获取我的个人信息
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                response['msg'] = "success"
                response['Nick'] = u.name
                response['Sex'] = u.gender
                response['Birthday'] = u.birthday
                response['Email'] = u.email
            else:
                response['msg'] = "cookie 过期了!"
        else:
            response['msg'] = "不存在这样的用户名！"
    except Exception as e:
        response['msg'] = str(e)
    return JsonResponse(response)


@require_http_methods(["GET"])
def Authentication(request):  # 身份认证
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                response['state'] = 1
                response['msg'] = "起飞！"
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


@require_http_methods(["POST"])
def uploadNewArticle(request):  # 上传自己新建的文档  个人的和团队的(文件名相同会覆盖，不相同创建新的)
    response = {}
    try:
        name = request.POST.get('name')
        token = request.POST.get('token')
        u = User.objects.get(name=name)
        content = request.POST.get('content')
        title = request.POST.get('title')
        message = request.POST.get('message')
        ifteam = request.POST.get('ifteam')
        ifteam = int(ifteam)
        visibility = request.POST.get('visibility')
        visibility = int(visibility)
        commentGranted = int(request.POST.get('commentGranted'))
        commentGranted = commentGranted > 0

        if u:  # 用户存在
            if UserToken.objects.get(user=u, token=token):  # 认证成功
                article = Article()
                response['state'] = 1
                article.title = title
                article.tid = ifteam
                article.uid = u
                article.content = content
                article.visibility = visibility
                article.commentGranted = commentGranted
                article.message = message
                if ifteam > 0:
                    article.isTeamarticle = True
                article.save()
                response['msg'] = "起飞"
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


@require_http_methods(["GET"])
def getAllArticle(request):  # 我创建的全部文档的信息(不包含文档内容)个人和团队
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                response['state'] = 1
                articles = Article.objects.filter(uid=u, isAbandoned=False)
                response['articles'] = json.loads(serializers.serialize("json", articles))
                response['msg'] = "起飞"
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


@require_http_methods(["GET"])
def judgeRepetitiveArticleName(request):  # 判断是否有同名的个人或者团队文档
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        tid = request.GET['tid']
        tid = int(tid)
        title = request.GET['title']
        u = User.objects.get(name=name)

        if u:
            if UserToken.objects.get(user=u, token=token):
                if tid == -1 and Article.objects.filter(uid=u, title=title):
                    response['isRepetitiveArticleName'] = True
                elif tid > 0 and Article.objects.filter(uid=u, title=title):
                    response['isRepetitiveArticleName'] = True
                else:
                    response['isRepetitiveArticleName'] = False
                    response['msg'] = "起飞"
                    response['state'] = 1
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


@require_http_methods(["GET"])
def getArticleContent(request, id):  # 获取文章的内容
    response = {}
    try:
        id = int(id)
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)

        if u:
            if UserToken.objects.get(user=u, token=token):
                if Article.objects.filter(aid=id):  # 文章存在
                    article = Article.objects.filter(aid=id)[0]
                    if article.visibility >= 3 or article.uid == u:  # 可见
                        response['msg'] = "起飞"
                        response['content'] = article.content
                    elif article.isTeamarticle:
                        team = Team.objects.filter(tid=article.tid)
                        if article.isTeamarticle and article.visibility >= 1 and + \
                                MemberShip.objects.filter(team=team, user=article.uid) and + \
                                MemberShip.objects.filter(team=team, uid=article.u):
                            response['msg'] = "起飞"
                            response['content'] = article.content
                        else:
                            response['msg'] = "没有权限"
                    else:
                        response['msg'] = "没有权限"
                else:
                    response['msg'] = "文章不存在"
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 1
    return JsonResponse(response)


@require_http_methods(["GET"])
def deleteArticle(request, id):
    id = int(id)
    response = {}
    print("----------------------------------")
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        aid = request.GET['aid']
        aid = int(aid)
        article = Article.objects.get(aid=aid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if article:
                    print("++++++++++++++++++++++++")
                    if article.uid == u or article.isTeamarticle == True and Team.objects.get(
                            tid=article.tid).creatorid == u.uid:
                        article.isAbandoned = True
                        response['state'] = 1
                        response['msg'] = "起飞！"
                    else:
                        response['state'] = 0
                        response['msg'] = "宁无权删除此文件！"
                else:
                    response['state'] = 0
                    response['msg'] = "文章未找到！"
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)
