"""La definition des vues"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from . import settings
from .forms import DroneFlightCommentForm, DroneArticleCommentForm, DroneComponentCommentForm, \
    DroneConfigurationCommentForm
from .models import DroneArticle, DroneFlight, DroneConfiguration, DroneComponent
from .user_utils import user_is_moderator


def index(request):
    """
    Main Page
    :param request: the page request
    :return: the rendered page
    """
    if request.user.is_authenticated:
        articles = DroneArticle.objects.order_by('-date')[:15]
        return render(request, "drone/base_articles.html", {
            **settings.base_info,
            "page": "news",
            "articles": articles
        })
    else:
        return render(request, "drone/base_articles.html", {
            **settings.base_info,
            "page": "news", "articles": []
        })


@login_required
def detailed_article(request, article_id):
    """
    page for one article with details
    :param request: the page request
    :param article_id: the id of the article to find
    :return: the rendered page
    """
    article = get_object_or_404(DroneArticle, pk=article_id)
    new_comment = None
    # comment posted
    if request.method == "POST":
        comment_form = DroneArticleCommentForm(data=request.POST)
        if comment_form.is_valid():
            # create an object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # assign the comment to the current Article
            new_comment.article = article
            # assign the current user to the comment
            new_comment.auteur = request.user
            # mark it as active if the user is in Moderateurs group
            if user_is_moderator(request.user):
                new_comment.active = True
            # save it to database
            new_comment.save()
    else:
        comment_form = DroneArticleCommentForm()
    return render(request, "drone/detailed_article.html", {
        **settings.base_info,
        "page": "news",
        "article": article,
        "new_comment": new_comment,
        "comment_form": comment_form
    })


@login_required
def vols(request):
    """
    Main Page
    :param request: the page request
    :return: the rendered page
    """
    df = DroneFlight.objects.order_by("-date")
    return render(request, "drone/base_flight.html", {
        **settings.base_info,
        "page": "vols", "vols": df
    })


@login_required
def detailed_vol(request, vol_id):
    """
    page for one article with details
    :param request: the page request
    :param vol_id: the id of the flight to find
    :return: the rendered page
    """
    vol = get_object_or_404(DroneFlight, pk=vol_id)
    new_comment = None
    # comment posted
    if request.method == "POST":
        comment_form = DroneFlightCommentForm(data=request.POST)
        if comment_form.is_valid():
            # create an object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # assign the comment to the current Article
            new_comment.article = vol
            # assign the current user to the comment
            new_comment.auteur = request.user
            # mark it as active if the user is in Moderateurs group
            if user_is_moderator(request.user):
                new_comment.active = True
            # save it to database
            new_comment.save()
    else:
        comment_form = DroneFlightCommentForm()
    return render(request, "drone/detailed_flight.html", {
        **settings.base_info,
        "page": "vols",
        "vol": vol,
        "new_comment": new_comment,
        "comment_form": comment_form
    })


@login_required
def configurations(request):
    """
    Main Page
    :param request: the page request
    :return: the rendered page
    """
    dc = DroneConfiguration.objects.order_by('-version_number')
    return render(request, "drone/base_configuration.html", {
        **settings.base_info,
        "page": "confs", "configurations": dc
    })


@login_required
def detailed_configuration(request, conf_id):
    """
    page for one article with details
    :param request: the page request
    :param conf_id: the id of the article to find
    :return: the rendered page
    """
    dc = get_object_or_404(DroneConfiguration, pk=conf_id)
    new_comment = None
    # comment posted
    if request.method == "POST":
        comment_form = DroneConfigurationCommentForm(data=request.POST)
        if comment_form.is_valid():
            # create an object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # assign the comment to the current Article
            new_comment.article = dc
            # assign the current user to the comment
            new_comment.auteur = request.user
            # mark it as active if the user is in Moderateurs group
            if user_is_moderator(request.user):
                new_comment.active = True
            # save it to database
            new_comment.save()
    else:
        comment_form = DroneConfigurationCommentForm()
    return render(request, "drone/detailed_configuration.html", {
        **settings.base_info,
        "page": "confs",
        "conf": dc,
        "new_comment": new_comment,
        "comment_form": comment_form
    })


@login_required
def composants(request):
    """
    Main Page
    :param request: the page request
    :return: the rendered page
    """
    dc = DroneComponent.objects.order_by("titre")
    return render(request, "drone/base_composants.html", {
        **settings.base_info,
        "page": "comps", "composants": dc
    })


@login_required
def detailed_composant(request, comp_id):
    """
    page for one article with details
    :param request: the page request
    :param comp_id: the id of the article to find
    :return: the rendered page
    """
    dc = get_object_or_404(DroneComponent, pk=comp_id)
    new_comment = None
    # comment posted
    if request.method == "POST":
        comment_form = DroneComponentCommentForm(data=request.POST)
        if comment_form.is_valid():
            # create an object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # assign the comment to the current Article
            new_comment.article = dc
            # assign the current user to the comment
            new_comment.auteur = request.user
            # mark it as active if the user is in Moderateurs group
            if user_is_moderator(request.user):
                new_comment.active = True
            # save it to database
            new_comment.save()
    else:
        comment_form = DroneComponentCommentForm()
    return render(request, "drone/detailed_composant.html", {
        **settings.base_info,
        "page": "comps",
        "comp": dc,
        "new_comment": new_comment,
        "comment_form": comment_form
    })
