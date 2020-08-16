from django.core import serializers
import json
from django.http import HttpResponse, JsonResponse, FileResponse, Http404, StreamingHttpResponse
from .models import User, UserToken, Article, MemberShip, Team, PersonalMessage, TeamMessage, Comment, Tocomment, \
    BrowerHistory, Favorite
import uuid
from testapp import models
from datetime import datetime
# Create your views here.
from django.views.decorators.http import require_http_methods
from django.db.models import Q


def object_to_json(obj):
    return dict([(kk, obj.__dict__[kk]) for kk in obj.__dict__.keys() if kk != "_state"])


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
        commentGranted = commentGranted > 0
        print("------------------------------")
        print(ifteam)
        print(title)
        if u:  # 用户存在
            if UserToken.objects.get(user=u, token=token):  # 认证成功
                if aid == -1:  # 新建文章
                    article = Article()
                    response['msg'] = "创建了一个新文档"
                else:
                    article = Article.objects.get(aid=aid)
                    response['msg'] = "修改了一个已存在的文档"
                response['state'] = 1
                article.title = title
                article.tid = ifteam
                article.uid = u
                if content != "null":
                    article.content = content
                article.visibility = visibility
                article.commentGranted = commentGranted
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
                        if Article.objects.filter(uid=u, title=title):  # 重复
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


# 获取文章内容
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
                        response['msg'] = "起飞"
                        author = article.uid.name
                        response['author'] = author
                        response['article'] = object_to_json(article)
                        response['content'] = article.content
                    elif article.isTeamarticle:
                        team = Team.objects.filter(tid=article.tid)
                        if article.isTeamarticle and article.visibility >= 1 and + \
                                MemberShip.objects.filter(team=team, user=article.uid) and + \
                                MemberShip.objects.filter(team=team, uid=u):
                            response['msg'] = "起飞"
                            author = article.uid.name
                            response['author'] = author
                            response['content'] = article.content
                            response['article'] = object_to_json(article)
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
                    response['state'] = 0
                elif newEmail != u.email and User.objects.filter(email=newEmail):
                    response['msg'] = "邮箱已存在，请更换邮箱"
                    response['state'] = 0
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
                response['state'] = 0
        else:
            response['msg'] = "不存在这样的用户名！"
            response['state'] = 0
    except Exception as e:
        response['msg'] = str(e)
        response['state'] = 0
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
                userList = User.objects.filter(name__icontains=key)
                teamList = Team.objects.filter(tname__icontains=key)
                articleList = Article.objects.filter(title__icontains=key, visibility__gte=3)
                authorList = []
                for item in articleList:
                    authorName = item.uid.name
                    authorList.append(authorName)
                response['authorList'] = authorList
                response['userList'] = json.loads(serializers.serialize("json", userList))
                response['teamList'] = json.loads(serializers.serialize("json", teamList))
                response['articleList'] = json.loads(serializers.serialize("json", articleList))
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
                    messageToInviter.user = User.objects.get(uid=team.creatorid)
                    messageToInviter.type = "成员加入"
                    messageToInviter.content = str(name) + "同意了你的邀请，加入了您的团队[" + str(team.tname) +"]"
                    messageToInviter.save()
                    personalmessage.checked = True
                    personalmessage.save()
                    response['msg'] = "成功加入团队"
                else:
                    messageToInviter.user = User.objects.filter(uid=team.creatorid)[0]
                    messageToInviter.content = str(name) + "拒绝了你的邀请，没有加入您的团队[" + str(team.tname) +"]"
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
                messageList = PersonalMessage.objects.filter(user=u)
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
                for item in MemberShipList:
                    team = item.team
                    teamList.append(object_to_json(team))
                response['teamList'] = teamList
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
                ArticleList = Article.objects.filter(tid=tid)
                response['ArticleList'] = json.loads(serializers.serialize("json", ArticleList))
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
        if u:
            if UserToken.objects.get(user=u, token=token):
                tocomment = Tocomment()
                tocomment.user = u
                tocomment.comment = comment
                tocomment.content = content
                tocomment.save()
                response['state'] = 1
                response['msg'] = "评论成功！"
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


# @require_http_methods(["GET"])
# def exitTeam(request):


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
                    for it in sonComments: # id是子评论
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
