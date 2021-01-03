from .neo4j_utils import Neo, R_category
from SeriesRecommandation.settings import NEO4J_PASSWORD, NEO4J_USER
from .forms import RecommendationForm
from django.shortcuts import render, get_object_or_404, redirect

neo = Neo("bolt://149.156.109.37:7687", (NEO4J_USER, NEO4J_PASSWORD))


def index(request):
    return render(request, 'api/index.html')


def stylesheet(request):
    return render(request, '../static/api/main.css')

def cat(c):
    if c == 'a':
        return R_category.ACTOR
    if c == 'g':
        return R_category.GENRE
    if c == 'u':
        return R_category.USER
    return R_category.RANDOM


def recommendation(request, pk):
    user = request.user.username
    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            number = int(form.cleaned_data['number'])
            context = {}
            series, reason = neo.get_recommendation(user=user, category=cat(category), number_to_recommend=number)
            context['series'] = series
            context['reason'] = reason
            return render(request, "api/recommendation-result.html", context)
    else:
        form = RecommendationForm()
    return render(request, "api/recommendation.html", {'form': form})


def anime_list(request):
    user = request.user.username
    my_anime = neo.get_series(user=user)
    all_anime = neo.get_series()
    not_watched_anime = [x for x in all_anime if x not in my_anime]
    context = {
        'my_anime': my_anime,
        'new_anime': not_watched_anime,
    }
    return render(request, "api/my-anime.html", context)


def friend_list(request):
    user = request.user.username
    my_friends = neo.get_friends(user=user)
    all_users = neo.get_friends()
    not_befriended = [x for x in all_users if x not in my_friends and x != user]
    context = {
        'friends': my_friends,
        'strangers': not_befriended,
    }
    return render(request, "api/my-friends.html", context)


def anime_watch(request, anime):
    user = request.user.username
    neo.marked_as_watched(user, anime)
    my_anime = neo.get_series(user=user)
    all_anime = neo.get_series()
    not_watched_anime = [x for x in all_anime if x not in my_anime]
    context = {
        'my_anime': my_anime,
        'new_anime': not_watched_anime,
    }
    return render(request, "api/my-anime.html", context)


def anime_unwatch(request, anime):
    user = request.user.username
    neo.marked_as_unwatched(user, anime)
    my_anime = neo.get_series(user=user)
    all_anime = neo.get_series()
    not_watched_anime = [x for x in all_anime if x not in my_anime]
    context = {
        'my_anime': my_anime,
        'new_anime': not_watched_anime,
    }
    return render(request, "api/my-anime.html", context)


def befriend(request, friend):
    user = request.user.username
    neo.get_friendly(user, friend)
    my_friends = neo.get_friends(user=user)
    all_users = neo.get_friends()
    not_befriended = [x for x in all_users if x not in my_friends and x != user]
    context = {
        'friends': my_friends,
        'strangers': not_befriended,
    }
    return render(request, "api/my-friends.html", context)

def unfriend(request, friend):
    user = request.user.username
    neo.get_unfriendly(user, friend)
    my_friends = neo.get_friends(user=user)
    all_users = neo.get_friends()
    not_befriended = [x for x in all_users if x not in my_friends and x != user]
    context = {
        'friends': my_friends,
        'strangers': not_befriended,
    }
    return render(request, "api/my-friends.html", context)