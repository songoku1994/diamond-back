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
                response['imgurl'] = "http://127.0.0.1:8000/media/" + str(u.uphoto)
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
def uploadNewArticle(request):  # 上传自己的文档  个人的和团队的(文件名相同会覆盖，不相同创建新的)
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
        print("------------------------------")
        print(ifteam)
        print(title)
        if u:  # 用户存在
            if UserToken.objects.get(user=u, token=token):  # 认证成功
                if ifteam == -1 and Article.objects.filter(tid=-1, title=title, uid=u):
                    article = Article.objects.get(tid=ifteam, title=title, uid=u)
                    print("77777777777777777777777777777777")
                    article.content = content
                    article.save()
                    response['msg'] = "起飞"
                    response['state'] = 1
                elif ifteam >= 1 and Article.objects.filter(tid=ifteam, title=title):
                    article = Article.objects.get(tid=ifteam, title=title)
                    print("77777777777777777777777777777777")
                    article.content = content
                    article.save()
                    response['msg'] = "起飞"
                    response['state'] = 1
                else:
                    print("9999999999999999999999999999999999")
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
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        aid = int(id)
        print(aid)
        article = Article.objects.get(aid=aid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if article:
                    if article.uid == u or article.isTeamarticle == True and Team.objects.get(
                            tid=article.tid).creatorid == u.uid:
                        article.isAbandoned = True
                        article.save()
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


@require_http_methods(["GET"])
def getAbandonedArticle(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                response['state'] = 1
                articles = Article.objects.filter(uid=u, isAbandoned=True)
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
def articleRecover(request, id):
    id = int(id)
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        aid = int(id)
        print(aid)
        article = Article.objects.get(aid=aid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if article:
                    if article.uid == u or article.isTeamarticle == True and Team.objects.get(
                            tid=article.tid).creatorid == u.uid:
                        article.isAbandoned = False
                        article.save()
                        response['state'] = 1
                        response['msg'] = "起飞！"
                    else:
                        response['state'] = 0
                        response['msg'] = "宁无权恢复此文件！"
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


@require_http_methods(["POST"])
def changeUserInfo(request):
    response = {}
    try:
        name = request.POST.get('name')
        token = request.POST.get('token')
        u = User.objects.get(name=name)
        newName = request.POST.get('newname')
        newGender = request.POST.get('gender') == "true"
        newBirthday = request.POST.get('birthday')
        newEmail = request.POST.get('newemail')
        uphoto = request.FILES.get('uphoto', None)
        print(uphoto)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if newName != name and User.objects.filter(name=newName):
                    response['msg'] = "用户名已存在，请更换用户名"
                    response['state'] = 0
                elif newEmail != u.email and User.objects.filter(email=newEmail):
                    response['msg'] = "邮箱已存在，请更换邮箱"
                    response['state'] = 0
                else:
                    u.name = newName
                    u.email = newEmail
                    u.gender = newGender
                    u.birthday = newBirthday
                    u.tags = ""
                    u.uphoto = uphoto
                    u.save()
                    response['msg'] = "修改成功！"
                    response['newname'] = newName
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
def createTeam(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        tname = request.GET['tname']
        tintro = request.GET['tintro']
        tphoto = request.FILES.get('tphoto', "")
        if u:
            if UserToken.objects.get(user=u, token=token):
                if Team.objects.filter(tname=tname):
                    response['msg'] = "团队名已存在"
                    response['state'] = 0
                else:
                    team = Team()
                    team.tname = tname
                    team.tIntro = tintro
                    team.Teamphoto = tphoto
                    team.creatorid = u.uid
                    team.save()
                    membership = MemberShip()
                    membership.user = u
                    membership.team = team
                    membership.save()
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
