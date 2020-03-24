from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import requests
from bs4 import BeautifulSoup

# Create your views here.
from users.models import FavouriteProperty


def index(request):
    if True:
        keyword = request.GET['keyword']
        # sortby = request.GET['sortby']
        filterby = request.GET['filterby']

        res = requests.get("https://developers.onemap.sg/commonapi/search?returnGeom=Y&getAddrDetails=Y&pageNum=1",
                           params={'searchVal': keyword}).json()

        resfiltered = [i for i in res.get('results') if not (i['POSTAL'] == 'NIL')]

        for i in resfiltered:
            if i['BUILDING'] == 'NIL':
                i['BUILDING'] = i['ADDRESS']
            # Python program to scrape website
            # and save quotes from website
            name = i['BUILDING'].replace(" ", "-")
            URL = "https://www.squarefoot.com.sg/trends-and-analysis/residential?p={}".format(name)
            URLL = "https://www.squarefoot.com.sg/trends-and-analysis/landed?p={}".format(name)

            try:
                r = requests.get(URL)
                info_raw = BeautifulSoup(r.content).find('table', {"class": "minimalist", "width": "95%"}).text.replace(
                    "\n\n", "").replace("#", "").replace("*", "").split("\n")
                ptype = "Non-Landed Residential"
            except:
                try:
                    r = requests.get(URLL)
                    info_raw = BeautifulSoup(r.content).find('table',
                                                             {"class": "minimalist", "width": "95%"}).text.replace(
                        "\n\n", "").replace("#", "").replace("*", "").split("\n")
                    ptype = "Landed Residential"
                except:
                    ptype = None

            i['TYPE'] = ptype

        if filterby == "nonlanded":
            resfiltered2 = [i for i in resfiltered if (i['TYPE'] == "Non-Landed Residential")]
        elif filterby == "landed":
            resfiltered2 = [i for i in resfiltered if (i['TYPE'] == "Landed Residential")]
        else:
            resfiltered2 = [i for i in resfiltered if not (i['TYPE'] == None)]

        context = {
            'keyword': keyword,
            'res': resfiltered2
        }
        return render(request, "search/index.html", context)
    # except KeyError:
    #    return HttpResponse("Access through home, please")


@login_required(login_url="/users/login")
def favourites_view(request):
    if request.POST:
        user = request.user
        if user is not None:
            propertyname=request.POST['propertyname']
            new_favourite = FavouriteProperty.objects.create(name=propertyname, user=user)
            new_favourite.save()
            next_url = request.POST.get('next', '/')
            if next_url != "/users/login":
                return HttpResponseRedirect(next_url)
        else:
            HttpResponseRedirect(request)
    else:
        return HttpResponseRedirect(request)
