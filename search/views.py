import requests
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from pandas import *

# Create your views here.
from users.models import FavouriteProperty


def index(request):
    if True:
        keyword = request.GET['keyword']
        filterby = request.GET['filterby']
        district = request.GET['district']

        if (keyword == 'nil') & (district != 'nil'):
            xls = ExcelFile("propertea/static/propertea.xlsx")
            data = xls.parse(xls.sheet_names[0])
            data = data.to_dict('index')
            values = [v for v in data.values()]
            resfiltered = [i for i in values if (i['DISTRICT'] == district)]

        else:
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
                    info_raw = BeautifulSoup(r.content).find('table',
                                                             {"class": "minimalist", "width": "95%"}).text.replace(
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

        seen = set()
        resfiltered2 = []
        for d in resfiltered:
            t = tuple(d['BUILDING'])
            if t not in seen:
                seen.add(t)
                resfiltered2.append(d)

        if filterby == "nonlanded":
            final = [i for i in resfiltered2 if (i['TYPE'] == "Non-Landed Residential")]
        elif filterby == "landed":
            final = [i for i in resfiltered2 if (i['TYPE'] == "Landed Residential")]
        else:
            final = [i for i in resfiltered2 if not (i['TYPE'] == None)]


        favourite = []
        if request.user.is_authenticated:
            favourite = [i[0] for i in list(request.user.favouriteproperty_set.values_list('name'))]
        print(favourite)

        context = {
            'keyword': keyword,
            'res': final,
            'district': district,
            'favourite': favourite,
        }
        return render(request, "search/index.html", context)
    # except KeyError:
    #    return HttpResponse("Access through home, please")


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
