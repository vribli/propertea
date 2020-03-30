import requests
from bs4 import BeautifulSoup
from pandas import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from users.models import FavouriteProperty



class SearchController:
    def __init__(self, request):
        self.keyword = request.GET['keyword']
        self.filterby = request.GET['filterby']
        self.district = request.GET['district']
        self.request = request

    def search(self):
        if (self.keyword == 'nil') & (self.district != 'nil'):
            result = self.searchByDistrict()
        else:
            result = self.searchByKeyword()
        return self.filter(result)

    def searchByDistrict(self):
        xls = ExcelFile("propertea/static/propertea.xlsx")
        data = xls.parse(xls.sheet_names[0])
        data = data.to_dict('index')
        return [i for i in data.values() if (i['DISTRICT'] == self.district)]

    def searchByKeyword(self):
        res = requests.get("https://developers.onemap.sg/commonapi/search?returnGeom=Y&getAddrDetails=Y&pageNum=1",
                           params={'searchVal': self.keyword}).json()
        resfiltered = [i for i in res.get('results') if not (i['POSTAL'] == 'NIL')]

        for i in resfiltered:
            if i['BUILDING'] == 'NIL':
                i['BUILDING'] = i['ADDRESS']
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

        return resfiltered2

    def filter(self, result):
        if self.filterby == "nonlanded":
            final = [i for i in result if (i['TYPE'] == "Non-Landed Residential")]
        elif self.filterby == "landed":
            final = [i for i in result if (i['TYPE'] == "Landed Residential")]
        else:
            final = [i for i in result if not (i['TYPE'] == None)]
        return final

    def favourite(self):
        favourite = []
        if self.request.user.is_authenticated:
            favourite = [i[0] for i in list(self.request.user.favouriteproperty_set.values_list('name'))]
        return favourite

    def getResponse(self):
        context = {
            'keyword': self.keyword,
            'res': self.search(),
            'district': self.district,
            'favourite': self.favourite(),
        }
        return render(self.request, "search/index.html", context)

    def favouriteResponse(self):
        if self.request.POST:
            user = self.request.user
            if user is not None:
                propertyname = self.request.POST['propertyname']
                favourite = []
                if self.request.user.is_authenticated:
                    favourite = [i[0] for i in list(self.request.user.favouriteproperty_set.values_list('name'))]
                if propertyname in favourite:
                    FavouriteProperty.objects.get(name=propertyname, user=user).delete()
                else:
                    new_favourite = FavouriteProperty.objects.create(name=propertyname, user=user)
                    new_favourite.save()
                next_url = self.request.POST.get('next', '/')
                if next_url != "/users/login":
                    return HttpResponseRedirect(next_url)
            else:
                HttpResponseRedirect(self.request)
        else:
            return HttpResponseRedirect(self.request)
