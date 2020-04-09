from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .controller import SearchController

# Create your views here.
from users.models import FavouriteProperty


def index(request):
    """
    This function seeks to access the 'index' page.

    :param request: The HTTP request at the instance
    :return: HTTP Response of getResponse()
    """
    c = SearchController(request)
    return c.getResponse()


@login_required(login_url="/users/login")
def favourites_view(request):
    """
    This function seeks to assist in the toggling of favourites.

    :param request: THe HTTP Request at the instance.
    :return: HTTP Response of favouriteResponse()
    """
    c = SearchController(request)
    return c.favouriteResponse()
