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
                    articleListt.append(object_to_json(article))
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
