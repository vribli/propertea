from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .controller import SearchController

# Create your views here.
from users.models import FavouriteProperty


def index(request):
    c = SearchController(request)

    context = {
        'keyword': c.keyword,
        'res': c.search(),
        'district': c.district,
        'favourite': c.favourite(),
    }
    return render(request, "search/index.html", context)


@login_required(login_url="/users/login")
def favourites_view(request):
    if request.POST:
        user = request.user
        if user is not None:
            propertyname = request.POST['propertyname']
            favourite = []
            if request.user.is_authenticated:
                favourite = [i[0] for i in list(request.user.favouriteproperty_set.values_list('name'))]
            if propertyname in favourite:
                FavouriteProperty.objects.get(name=propertyname, user=user).delete()
            else:
                new_favourite = FavouriteProperty.objects.create(name=propertyname, user=user)
                new_favourite.save()
            next_url = request.POST.get('next', '/')
            if next_url != "/users/login":
                return HttpResponseRedirect(next_url)
        else:
            HttpResponseRedirect(request)
    else:
        return HttpResponseRedirect(request)
