from django.core import serializers
import json

from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse, FileResponse, Http404, StreamingHttpResponse

from diamond import settings
from .models import User, UserToken, Article, MemberShip, Team, PersonalMessage, TeamMessage, Comment, Tocomment, \
    BrowerHistory, Favorite, Worktrend
import uuid
from testapp import models
from datetime import datetime
# Create your views here.
from django.views.decorators.http import require_http_methods
from django.db.models import Q


# response['articles'][0]['fields']['content']=""
def object_to_json(obj):
    return dict([(kk, obj.__dict__[kk]) for kk in obj.__dict__.keys() if kk != "_state"])


# 根据邮箱更改密码
@require_http_methods(["GET"])
def changePasswordByEmail(request):
    response = {}
    try:
        email = request.GET['email']
        newpassword = request.GET['newpassword']
        u = User.objects.get(email=email)
        if u:
            u.password = newpassword
            u.save()
            response['state'] = 1
        else:
            response['msg'] = "邮箱未注册过！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


def check_mail(request):
    response = {}
    try:
        email = request.GET['email']
        str = request.GET['str2']
        send_mail(
            subject='金刚石文档注册验证',
            message=str,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email]
        )
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


# 判断是否有重复的用户名：
@require_http_methods(["GET"])
def judgeRepetitiveUserName(request):
    response = {}
    name = request.GET["name"]
    if User.objects.filter(name=name):
        response['msg'] = "重复用户名"
        response['state'] = 0
    else:
        response['msg'] = "合法的用户名"
        response['state'] = 1
    return JsonResponse(response)


# 判断是否有重复的邮箱：
@require_http_methods(["GET"])
def judgeRepetitiveEmail(request):
    response = {}
    email = request.GET["email"]
    if User.objects.filter(email=email):
        response['msg'] = "重复邮箱"
        response['state'] = 0
    else:
        response['msg'] = "合法的邮箱"
        response['state'] = 1
    return JsonResponse(response)


# 注册
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


# 登录
@require_http_methods(["GET"])
def login(request):
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
                response['uid'] = user.uid
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


# 获取我的个人信息
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
                response['tags'] = u.tags
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


# 身份认证
@require_http_methods(["GET"])
def Authentication(request):
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


# 上传文件/编辑文件
@require_http_methods(["POST"])
def uploadNewArticle(request):
    response = {}
    try:
        name = request.POST.get('name')
        token = request.POST.get('token')
        u = User.objects.get(name=name)
        aid = request.POST.get('aid')
        aid = int(aid)
        content = request.POST.get('content')
        title = request.POST.get('title')
        message = request.POST.get('message')
        ifteam = request.POST.get('ifteam')
        ifteam = int(ifteam)
        visibility = request.POST.get('visibility')
        visibility = int(visibility)
        commentGranted = int(request.POST.get('commentGranted'))
        print(commentGranted)
        commentGranted = commentGranted > 0
        print("------------------------------")
        print(ifteam)
        print(title)
        if u:  # 用户存在
            if UserToken.objects.get(user=u, token=token):  # 认证成功
                if aid == -1:  # 新建文章
                    article = Article()
                    response['msg'] = "创建了一个新文档"
                    article.uid = u
                else:  # 编辑文章
                    article = Article.objects.get(aid=aid)
                    response['msg'] = "修改了一个已存在的文档"
                response['state'] = 1
                article.title = title
                article.tid = ifteam
                if content != "null":
                    article.content = content
                article.visibility = visibility
                article.commentGranted = commentGranted
                article.isEditing = True
                article.editorid = u.uid
                article.message = message
                if ifteam > 0:
                    article.isTeamarticle = True
                article.save()
                response['aid'] = article.aid
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


# 获取我的文章列表
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
                articles = Article.objects.filter(uid=u, isAbandoned=False, tid=-1).order_by('-lastedittime')
                for item in articles:
                    item.content = ""
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


# 判断文章名是否重复 ~Q是取反的意思
@require_http_methods(["GET"])
def judgeRepetitiveArticleName(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        tid = request.GET['tid']
        tid = int(tid)
        aid = request.GET['aid']
        aid = int(aid)
        title = request.GET['title']
        u = User.objects.get(name=name)

        if u:
            if UserToken.objects.get(user=u, token=token):
                if tid == -1:  # 个人文章
                    if aid == -1:  # 新建文章
                        if Article.objects.filter(uid=u, title=title, tid=-1):  # 重复
                            response['isRepetitiveArticleName'] = True
                        else:
                            response['isRepetitiveArticleName'] = False
                            response['msg'] = "起飞"
                            response['state'] = 1
                    elif Article.objects.filter(uid=u, title=title).filter(~Q(aid=aid)):
                        response['isRepetitiveArticleName'] = True
                    else:
                        response['isRepetitiveArticleName'] = False
                        response['msg'] = "起飞"
                        response['state'] = 1
                elif aid == -1:  # 团队文章 新建
                    if Article.objects.filter(tid=tid, title=title):
                        response['isRepetitiveArticleName'] = True
                    else:
                        response['isRepetitiveArticleName'] = False
                        response['msg'] = "起飞"
                        response['state'] = 1
                elif aid >= 1:  # 团队文章 修改
                    if Article.objects.filter(tid=tid, title=title).filter(~Q(aid=aid)):
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


# 获取文章内容  在这里生成浏览记录
@require_http_methods(["GET"])
def getArticleContent(request, id):
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
                        print("++++++++++++++++++++++++++++++++++++++")
                        response['msg'] = "起飞"
                        author = article.uid.name
                        response['author'] = author
                        response['article'] = object_to_json(article)
                        response['content'] = article.content
                        if BrowerHistory.objects.filter(user=u, article=article):
                            history = BrowerHistory.objects.filter(user=u, article=article)[0]
                            history.save()
                        else:
                            history = BrowerHistory()
                            history.article = article
                            history.user = u
                            history.save()
                    elif article.isTeamarticle:
                        print("------------------------------------------")
                        team = Team.objects.filter(tid=article.tid)[0]
                        if article.visibility >= 1 and MemberShip.objects.filter(team=team,
                                                                                 user=article.uid) and MemberShip.objects.filter(
                            team=team, user=u):
                            print("*******************")
                            response['msg'] = "起飞"
                            author = article.uid.name
                            response['author'] = author
                            response['content'] = article.content
                            response['article'] = object_to_json(article)
                            if BrowerHistory.objects.filter(user=u, article=article):
                                history = BrowerHistory.objects.filter(user=u, article=article)[0]
                                history.save()
                            else:
                                history = BrowerHistory()
                                history.article = article
                                history.user = u
                                history.save()
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


# 文章放入回收站
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


# 获取回收站文章
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
                for item in articles:
                    item.content = ""
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


# 文章从回收站恢复
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


# 修改个人信息
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
        tags = request.POST.get('tags', "")
        print(uphoto)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if newName != name and User.objects.filter(name=newName):
                    response['msg'] = "用户名已存在，请更换用户名"
                    response['state'] = 404
                elif newEmail != u.email and User.objects.filter(email=newEmail):
                    response['msg'] = "邮箱已存在，请更换邮箱"
                    response['state'] = 405
                else:
                    u.name = newName
                    u.email = newEmail
                    u.gender = newGender
                    u.birthday = newBirthday
                    if tags != "":
                        u.tags = tags
                    if uphoto is not None:
                        u.uphoto = uphoto
                    u.save()
                    response['msg'] = "修改成功！"
                    response['newname'] = newName
                    response['state'] = 1
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 406
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 407
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 408
    return JsonResponse(response)


# 创建团队
@require_http_methods(["POST"])
def createTeam(request):
    response = {}
    try:
        name = request.POST.get('name')
        token = request.POST.get('token')
        u = User.objects.get(name=name)
        tname = request.POST.get('tname')
        tintro = request.POST.get('tintro', "")
        tphoto = request.FILES.get('tphoto', None)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if Team.objects.filter(tname=tname):
                    response['msg'] = "团队名已存在"
                    response['state'] = 0
                else:
                    team = Team()
                    team.tname = tname
                    if tphoto is not None:
                        team.Teamphoto = tphoto
                    if tintro != "":
                        team.tIntro = tintro
                    team.creatorid = u.uid
                    team.membernumber = 1
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


# 彻底删除文件
@require_http_methods(["GET"])
def completelyDeleteArticle(request, id):
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
                        if article.isTeamarticle:
                            worktrend = Worktrend()
                            worktrend.user = u
                            worktrend.article = article
                            worktrend.team = Team.objects.get(tid=article.tid)
                            worktrend.content = str(u.name) + "删除了" + str(article.uid.name) + "创建的文章" + str(
                                article.title)
                            worktrend.save()
                        article.delete()
                        response['state'] = 1
                        response['msg'] = "彻底删除成功！"
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


# 获取文章、用户、团队列表
@require_http_methods(["GET"])
def getListByKey(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        key = request.GET['key']
        if u:
            if UserToken.objects.get(user=u, token=token):
                userList = User.objects.filter(name__icontains=key).order_by('name')
                teamList = Team.objects.filter(tname__icontains=key).order_by('tname')
                articleList = Article.objects.filter(title__icontains=key, visibility__gte=3,
                                                     isAbandoned=False).order_by('title')
                authorList = []
                for item in articleList:
                    authorName = item.uid.name
                    authorList.append(authorName)
                    item.content = ""
                response['authorList'] = authorList
                response['userList'] = json.loads(serializers.serialize("json", userList))
                response['teamList'] = json.loads(serializers.serialize("json", teamList))
                response['articleList'] = json.loads(serializers.serialize("json", articleList))
                print(response['articleList'][0]['fields'])
                response['state'] = 1
                response['msg'] = "成功根据关键字查询到列表！"
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


# 邀请用户加入我的团队
@require_http_methods(["GET"])
def inviteUserToTeam(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        uid = request.GET['uid']
        tid = request.GET['tid']
        invitedUser = User.objects.get(uid=uid)
        team = Team.objects.get(tid=tid)
        if u:
            if UserToken.objects.filter(user=u, token=token):
                if MemberShip.objects.filter(user=invitedUser, team=team):
                    response['msg'] = "该用户已在您的团队中"
                    response['state'] = 0
                elif PersonalMessage.objects.filter(tid=tid, user=invitedUser, isInviteMessage=True, checked=False):
                    response['msg'] = "不要重复发送邀请"
                    response['state'] = 0
                else:
                    newPersonalMessage = PersonalMessage()
                    newPersonalMessage.user = invitedUser
                    newPersonalMessage.isInviteMessage = True
                    newPersonalMessage.tid = tid
                    newPersonalMessage.type = "团队邀请"
                    newPersonalMessage.content = str(u.name) + "邀请您加入团队" + str(team.tname)
                    newPersonalMessage.save()
                    response['msg'] = "已经向该用户发出邀请！"
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


# 接受邀请加入团队
@require_http_methods(["GET"])
def AcceptToJoinTeam(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        pmid = request.GET['pmid']
        tid = request.GET['tid']
        team = Team.objects.get(tid=tid)
        personalmessage = PersonalMessage.objects.get(pmid=pmid)
        Accepted = request.GET['Accept'] == "true"
        messageToInviter = PersonalMessage()
        if u:
            if UserToken.objects.get(user=u, token=token):
                if Accepted:
                    newmembership = MemberShip()
                    newmembership.user = u
                    newmembership.team = team
                    newmembership.save()
                    team.membernumber += 1
                    team.save()
                    messageToInviter.user = User.objects.get(uid=team.creatorid)
                    messageToInviter.type = "成员加入"
                    messageToInviter.content = str(name) + "同意了你的邀请，加入了您的团队[" + str(team.tname) + "]"
                    messageToInviter.save()
                    personalmessage.checked = True
                    personalmessage.save()
                    response['msg'] = "成功加入团队"
                else:
                    messageToInviter.user = User.objects.filter(uid=team.creatorid)[0]
                    messageToInviter.content = str(name) + "拒绝了你的邀请，没有加入您的团队[" + str(team.tname) + "]"
                    messageToInviter.type = "邀请被拒绝"
                    messageToInviter.save()
                    personalmessage.checked = True
                    personalmessage.save()
                    response['msg'] = "成功拒绝了" + str(User.objects.get(uid=team.creatorid).name) + "的邀请"
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


# 我的消息
@require_http_methods(["GET"])
def myMessage(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                messageList = PersonalMessage.objects.filter(user=u).order_by('-time')
                response['message'] = json.loads(serializers.serialize("json", messageList))
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


# 把未读的消息设为已读（邀请加入团队 的信息在AcceptToJoinTeam中会自动设置为已读，不用再手动设为已读）
@require_http_methods(["GET"])
def checkMessage(request):  # 把消息设置为已读
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        pmid = request.GET['pmid']
        message = PersonalMessage.objects.get(pmid=pmid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                message.checked = True
                message.save()
                response['state'] = 1
                response['msg'] = "成功设置为已读！"
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


# 删除一条已读消息
@require_http_methods(["GET"])
def deleteMessage(request):  # 删除一个已读信息
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        pmid = request.GET['pmid']
        message = PersonalMessage.objects.get(pmid=pmid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                message.delete()
                response['state'] = 1
                response['msg'] = "成功设置为已读！"
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


# 获取我的团队
@require_http_methods(["GET"])
def myTeam(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                MemberShipList = MemberShip.objects.filter(user=u)
                teamList = []
                teamCreatorList = []
                for item in MemberShipList:
                    team = item.team
                    teamList.append(object_to_json(team))
                    tleadername = User.objects.get(uid=team.creatorid).name
                    teamCreatorList.append(tleadername)
                response['teamList'] = teamList
                response['teamCreatorList'] = teamCreatorList
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


# 获取团队成员
@require_http_methods("GET")
def getTeamMembers(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        tid = request.GET['tid']
        team = Team.objects.get(tid=tid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                MemberShipList = MemberShip.objects.filter(team=team)
                UserList = []
                for item in MemberShipList:
                    user = item.user
                    UserList.append(object_to_json(user))
                response['userList'] = UserList
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


# 获取团队文档
@require_http_methods("GET")
def getTeamArticles(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        tid = request.GET['tid']
        if u:
            if UserToken.objects.get(user=u, token=token):
                ArticleList = Article.objects.filter(tid=tid).order_by('lastedittime')
                authorList = []
                for item in ArticleList:
                    item.content = ""
                    authorList.append(item.uid.name)
                response['ArticleList'] = json.loads(serializers.serialize("json", ArticleList))
                response['authorList'] = authorList
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


# 对文章写评论  ，能否评论应该在前端判断
@require_http_methods(["GET"])
def createComment(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                aid = request.GET['aid']
                article = Article.objects.get(aid=aid)
                content = request.GET['content']
                comment = Comment()
                comment.article = article
                comment.uid = u
                comment.content = content
                comment.save()
                response['state'] = 1
                response['msg'] = "评论成功！"
                newMessage = PersonalMessage()
                newMessage.isInviteMessage = False
                newMessage.type = "文章被评论"
                newMessage.user = article.uid
                newMessage.content = "你的文章" + str(article.title) + "被" + str(u.name) + "评论了，快去看看吧！"
                newMessage.aid = aid
                newMessage.save()
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


# 对于评论写评论
@require_http_methods(["GET"])
def createToComment(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        cid = request.GET['cid']
        comment = Comment.objects.get(cid=cid)
        content = request.GET['content']
        article = comment.article
        if u:
            if UserToken.objects.get(user=u, token=token):
                tocomment = Tocomment()
                tocomment.user = u
                tocomment.comment = comment
                tocomment.content = content
                tocomment.save()
                response['state'] = 1
                response['msg'] = "评论成功！"
                newMessage = PersonalMessage()
                newMessage.user = comment.uid
                newMessage.isInviteMessage = False
                newMessage.type = "评论被评论"
                newMessage.content = "你在文章" + str(article.title) + "下的评论被" + str(u.name) + "评论了，快去看看吧！"
                newMessage.save()
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
def allFavorite(request):  # 显示出我收藏的文档
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                response['state'] = 1
                favoriteList = Favorite.objects.filter(user=u).order_by('-favoriteTime')
                articleList = []
                for item in favoriteList:
                    article = item.article
                    articleList.append(object_to_json(article))
                response['articleList'] = articleList
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


# 退出团队
@require_http_methods(["GET"])
def exitTeam(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        tid = request.GET['tid']
        uid = request.GET['uid']
        uid = int(uid)
        team = Team.objects.get(tid=tid)
        u = User.objects.get(name=name)
        u1 = User.objects.get(uid=uid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                membership = MemberShip.objects.get(user=u1, team=team)
                membership.delete()
                articles = Article.objects.filter(uid=u1, tid=team.tid)
                for item in articles:
                    item.uid = User.objects.filter(uid=team.creatorid)[0]
                    item.save()
                team.membernumber -= 1
                team.save()
                response['state'] = 1
                response['msg'] = "退出成功！"
                newMessage = PersonalMessage()
                if u1 == u:  # 自己退群，给群主发消息
                    newMessage.type = "群成员退出"
                    newMessage.user = User.objects.filter(uid=team.creatorid)[0]
                    newMessage.isInviteMessage = False
                    newMessage.content = "群成员" + str(u1.name) + "退出了您的团队" + str(team.tname)
                    newMessage.save()
                else:  # 踢人，给被踢的人发消息
                    newMessage.type = "被移出团队"
                    newMessage.user = u1
                    newMessage.isInviteMessage = False
                    newMessage.content = "你被团队" + str(team.tname) + "的创建者" + str(u.name) + "移出了团队"
                    newMessage.save()
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


# 获取文章 的评论信息
@require_http_methods(["GET"])
def getCommentsOfArticle(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        aid = request.GET['aid']
        aid = int(aid)
        article = Article.objects.get(aid=aid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                commentList = Comment.objects.filter(article=article)
                SonComments = []
                commenter = []
                SonCommenter = []
                for item in commentList:
                    sonComments = Tocomment.objects.filter(comment=item)
                    lucky = []
                    for it in sonComments:  # id是子评论
                        lucky.append(it.user.name)
                    SonCommenter.append(lucky)
                    SonComments.append(json.loads(serializers.serialize("json", sonComments)))
                    commenter.append(item.uid.name)
                response['commenter'] = commenter
                response['soncommenter'] = SonCommenter
                response['commentList'] = json.loads(serializers.serialize("json", commentList))
                response['SonComments'] = SonComments
                response['msg'] = "已获取此文章的评论和子评论"
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


# 搜成员，团队拉人的时候用
@require_http_methods(["GET"])
def getUserByKey(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        key = request.GET['key']
        tid = request.GET['tid']
        tid = int(tid)
        team = Team.objects.get(tid=tid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                userList = User.objects.filter(name__icontains=key)
                response['userList'] = json.loads(serializers.serialize("json", userList))
                response['state'] = 1
                response['msg'] = "成功根据关键字查询到列表！"
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 0
        else:
            response['msg'] = "不存在"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


# 解散团队
@require_http_methods(["GET"])
def DisbandTeam(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        tid = request.GET['tid']
        team = Team.objects.get(tid=tid)
        u = User.objects.get(name=name)
        creator = User.objects.get(uid=team.creatorid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                memberships = MemberShip.objects.filter(team=team)
                for item in memberships:
                    if item.user != creator:

                        newMessage = PersonalMessage()
                        newMessage.user = item.user
                        newMessage.type = "团队被解散"
                        newMessage.isInviteMessage = False
                        newMessage.content = "你所在的团队" + str(team.tname) + "已被创建者" + str(creator.name) + "解散，人生有梦，各自精彩"
                        newMessage.save()
                    else:
                        newMessage = PersonalMessage()
                        newMessage.user = creator
                        newMessage.type = "团队被解散"
                        newMessage.isInviteMessage = False
                        newMessage.content = "你所在的团队" + str(team.tname) + "已被创建者" + str(
                            creator.name) + "(你自己)解散，人生有梦，各自精彩"
                        newMessage.save()
                articles = Article.objects.filter(tid=team.tid)
                memberships.delete()
                articles.delete()
                team.delete()
                response['state'] = 1
                response['msg'] = "解散团队成功，人生有梦，各自精彩！"
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


# 获取浏览记录
@require_http_methods(["GET"])
def getBrowerHistory(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                historyList = BrowerHistory.objects.filter(user=u).order_by('-browertime')
                articleList = []
                authorList = []
                for item in historyList:
                    item.article.content = ""
                    articleList.append(object_to_json(item.article))
                    authorList.append(item.article.uid.name)
                response['authorList'] = authorList
                response['articleList'] = articleList
                response['historyList'] = json.loads(serializers.serialize("json", historyList))
                response['msg'] = "成功获取到浏览记录"
                response['state'] = 0
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


# 删除浏览记录
@require_http_methods(["GET"])
def deleteBrowerHistory(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        BHid = request.GET["bhid"]
        if u:
            if UserToken.objects.get(user=u, token=token):
                history = BrowerHistory.objects.get(BHid=BHid)
                history.delete()
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


# 通过id获取个人信息
@require_http_methods(["GET"])
def getUserInfoByID(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        id = request.GET['id']
        if u:
            if UserToken.objects.get(user=u, token=token):
                user = User.objects.get(uid=id)
                response['userInfo'] = object_to_json(user)
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
def deleteFavorite(request):  # 删除一个收藏
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        id = request.GET['id']
        u = User.objects.get(name=name)
        aid = int(id)
        print(id)
        article = Article.objects.get(aid=aid)
        favorite = Favorite.objects.get(user=u, article=article)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if favorite:
                    favorite.delete()
                    response['state'] = 1
                    response['msg'] = "起飞！"
                else:
                    response['state'] = 0
                    response['msg'] = "收藏未找到！"
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


# 收藏一个文档
@require_http_methods(["GET"])
def addFavorite(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        aid = request.GET['aid']
        u = User.objects.get(name=name)
        article = Article.objects.get(aid=aid)
        if u:  # 用户存在
            if UserToken.objects.get(user=u, token=token):  # 认证成功
                favorite = Favorite()
                favorite.user = u
                favorite.article = article
                favorite.save()
                response['msg'] = "起飞"
                response['state'] = 1
                newMessage = PersonalMessage()
                newMessage.type = "文章被收藏"
                newMessage.user = article.uid
                newMessage.isInviteMessage = False
                newMessage.content = "您的文章" + str(article.title) + "已被" + str(u.name) + "收藏，感谢您输出优质内容！"
                newMessage.save()
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


# 判断是否收藏
@require_http_methods(["GET"])
def judgeFavorite(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        aid = request.GET['aid']
        u = User.objects.get(name=name)
        article = Article.objects.get(aid=aid)
        if u:  # 用户存在
            if UserToken.objects.get(user=u, token=token):  # 认证成功
                if Favorite.objects.filter(user=u, article=article):
                    response['msg'] = True  # 已有收藏
                else:
                    response['msg'] = False  # 还未收藏
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


# 显示出我收藏的文档
@require_http_methods(["GET"])
def allFavorite(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                response['state'] = 1
                favoriteList = Favorite.objects.filter(user=u)
                articleList = []
                for item in favoriteList:
                    article = item.article
                    articleList.append(object_to_json(article))
                response['articleList'] = articleList
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


# 修改密码
@require_http_methods(["GET"])
def changePassword(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        password = request.GET['password']
        newpassword = request.GET['newpassword']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if u.password == password:
                    u.password = newpassword
                    u.save()
                    response['msg'] = "密码修改成功"
                    response['state'] = 1
                else:
                    response['msg'] = "请输入正确的原密码！"
                    response['state'] = 2
            else:
                response['msg'] = "cookie 过期了!"
                response['state'] = 3
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 4
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 5
    return JsonResponse(response)


# 修改团队信息
@require_http_methods(["POST"])
def changeTeamInfo(request):
    response = {}
    try:
        name = request.POST.get('name')
        token = request.POST.get('token')
        u = User.objects.get(name=name)
        tid = request.POST.get('tid')
        tid = int(tid)
        team = Team.objects.get(tid=tid)
        tname = request.POST.get('tname')
        tintro = request.POST.get('tintro', "")
        tphoto = request.FILES.get('tphoto', None)
        if u:
            if UserToken.objects.get(user=u, token=token):
                if Team.objects.filter(tname=tname) and team.tname != tname:
                    response['msg'] = "团队名已存在"
                    response['state'] = 0
                else:
                    team.tname = tname
                    if tphoto is not None:
                        team.Teamphoto = tphoto
                    if tintro != "":
                        team.tIntro = tintro
                    team.save()
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


# 上传修改状态
@require_http_methods(["GET"])
def beginEdit(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        aid = request.GET['aid']
        aid = int(aid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                article = Article.objects.get(aid=aid)
                article.isEditing = True
                article.editorid = u.uid
                article.save()
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


# 结束修改状态
@require_http_methods(["GET"])
def endEdit(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        aid = request.GET['aid']
        aid = int(aid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                article = Article.objects.get(aid=aid)
                article.editorid = -1
                article.isEditing = False
                article.save()
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


# 判断是否处于编辑状态
@require_http_methods(["GET"])
def judgeIfEditing(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        aid = request.GET['aid']
        aid = int(aid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                article = Article.objects.get(aid=aid)
                response['isEditing'] = article.isEditing
                if article.isEditing:
                    response['editor'] = User.objects.get(uid=article.editorid).name
                    response['msg'] = "用户" + str(User.objects.get(uid=article.editorid).name) + "正在编辑这篇文章"
                else:
                    response['msg'] = "这篇文章没有处于编辑状态，您可以编辑这篇文章"
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


# 获取团队的工作动态
@require_http_methods(["GET"])
def getTeamWorkTrend(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        tid = request.GET['tid']
        tid = int(tid)
        team = Team.objects.get(tid=tid)
        if u:
            if UserToken.objects.get(user=u, token=token):
                worktrendlist = Worktrend.objects.filter(team=team).order_by('-time')
                articleList = []
                namelist = []
                for item in worktrendlist:
                    namelist.append(item.user.name)
                    articleList.append(item.article.title)
                response['namelist'] = namelist
                response['articleList'] = articleList
                for item in worktrendlist:
                    item.article.content = ""
                response['worktrendlist'] = json.loads(serializers.serialize("json", worktrendlist))
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


# 上传工作动态
@require_http_methods(["GET"])
def uploadWorkTrend(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        tid = request.GET['tid']
        tid = int(tid)
        aid = request.GET['aid']
        aid = int(aid)
        article = Article.objects.get(aid=aid)
        team = Team.objects.get(tid=tid)
        content = request.GET['content']
        if u:
            if UserToken.objects.get(user=u, token=token):
                if content != "":
                    worktrend = Worktrend()
                    worktrend.article = article
                    worktrend.team = team
                    worktrend.user = u
                    worktrend.content = content
                    worktrend.save()
            else:
                response['msg'] = "cookie过期了！"
                response['state'] = 0

        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)


# 获取未读消息数
@require_http_methods(["GET"])
def getMessagenum(request):
    response = {}
    try:
        name = request.GET['name']
        token = request.GET['token']
        u = User.objects.get(name=name)
        if u:
            if UserToken.objects.get(user=u, token=token):
                list = PersonalMessage.objects.filter(user=u, checked=False)
                messagenum = 0
                for _ in list:
                    messagenum = messagenum + 1
                response['messagenum'] = messagenum
            else:
                response['msg'] = "cookie过期了！"
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
    return JsonResponse(response)
