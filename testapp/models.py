from django.db import models
from tinymce.models import HTMLField


class User(models.Model):
    uid = models.AutoField(primary_key=True)  # 用户id，主键
    name = models.CharField(blank=False, null=False, max_length=100)  # 用户名
    gender = models.BooleanField(default=False)  # 性别
    email = models.EmailField(blank=False, null=False)
    birthday = models.DateField(default="2000-1-1")
    password = models.CharField(max_length=30, null=False, blank=False, default="a12345678")
    tags = models.TextField(default="")
    uphoto = models.ImageField(upload_to="uphoto/", default="uphoto/default.jpg")  # 头像
    createtime = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserToken(models.Model):
    user = models.OneToOneField(to='User', on_delete=models.CASCADE)
    token = models.CharField(max_length=64)


class Article(models.Model):
    aid = models.AutoField(primary_key=True)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(blank=False, null=False, max_length=100)
    content = HTMLField()
    tid = models.IntegerField(default=-1)
    message = models.CharField(default="", max_length=200)
    isTeamarticle = models.BooleanField(default=False)
    isAbandoned = models.BooleanField(default=False)
    visibility = models.IntegerField(default=1)
    commentGranted = models.BooleanField(default=True)
    createtime = models.DateTimeField(auto_now_add=True)
    lastedittime = models.DateTimeField(auto_now=True)
    isEditing = models.BooleanField(default=False)
    editorid = models.IntegerField(default=-1)

    def __str__(self):
        return self.title


class Team(models.Model):
    tid = models.AutoField(primary_key=True)
    creatorid = models.IntegerField()
    membernumber = models.IntegerField(default=0)
    createtime = models.DateTimeField(auto_now_add=True)
    tname = models.CharField(blank=False, null=False, max_length=100)
    tIntro = models.CharField(max_length=200)
    Teamphoto = models.ImageField(upload_to="Tphoto/", default="Tphoto/default.jpg")  # 头像

    def __str__(self):
        return self.tname


class MemberShip(models.Model):
    mid = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    participateTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.tid) + '/' + str(self.uid)


class Comment(models.Model):
    cid = models.AutoField(primary_key=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    commentTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.cid)


class Tocomment(models.Model):
    tcid = models.AutoField(primary_key=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    commentTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.tcid)


class Favorite(models.Model):
    fid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    favoriteTime = models.DateTimeField(auto_now_add=True)


# browserHistory(BHid,uid,aid，time)
class BrowerHistory(models.Model):
    BHid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    browertime = models.DateTimeField(auto_now=True)


class PersonalMessage(models.Model):
    # 个人的消息应该包括：被邀请加入团队，被踢出团队，文章被评论，文章被转发，评论被评论，有人接受了我的邀请，
    # 有人拒绝了我的邀请，有人自己退出了我的团队
    pmid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    tid = models.IntegerField(default=-1)
    aid = models.IntegerField(default=-1)
    type = models.CharField(default="", max_length=200)
    isInviteMessage = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)


class TeamMessage(models.Model):
    tmid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)


class Worktrend(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
