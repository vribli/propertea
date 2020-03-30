from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .controller import SearchController

# Create your views here.
from users.models import FavouriteProperty


def index(request):
    c = SearchController(request)
    return c.getResponse()


@login_required(login_url="/users/login")
def favourites_view(request):
    c = SearchController(request)
    return c.favouriteResponse()
