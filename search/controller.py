import requests
from bs4 import BeautifulSoup
from pandas import *
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from users.models import FavouriteProperty



class SearchController:
    """
    This controller class executes the logic for the 'Search' sub-application
    """
    def __init__(self, request):
        self.keyword = request.GET['keyword']
        self.filterby = request.GET['filterby']
        self.district = request.GET['district']
        self.request = request

    def search(self):
        """
        This function implements logic for the 'Search Results' page.

        :return: Calls the relavant functions based on user request.
        """
        if (self.keyword == 'nil') & (self.district != 'nil'):
            result = self.searchByDistrict()
        else:
            result = self.searchByKeyword()
        return self.filter(result)

    def searchByDistrict(self):
        """
        This function implements logic for searching by district.

        :return: List of Properties in the district based on the CSV.
        """
        xls = ExcelFile("propertea/static/propertea.xlsx")
        data = xls.parse(xls.sheet_names[0])
        data = data.to_dict('index')
        return [i for i in data.values() if (i['DISTRICT'] == self.district)]

    def searchByKeyword(self):
        """
        This function implements logic for searching by keyword.

        :return: List of Properties related to the specific keyword.
        """
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
        """
        This function implements logic for filtering the results obtained.

        :param result: The result obtained via Search.
        :return: The filtered result based on the initial result.
        """
        if self.filterby == "nonlanded":
            final = [i for i in result if (i['TYPE'] == "Non-Landed Residential")]
        elif self.filterby == "landed":
            final = [i for i in result if (i['TYPE'] == "Landed Residential")]
        else:
            final = [i for i in result if not (i['TYPE'] == None)]
        return final

    def favourite(self):
        """
        This function implements logic for toggling the favourites button.

        :return: The list of Favourite Properties in the database for a particular user.
        """
        favourite = []
        if self.request.user.is_authenticated:
            favourite = [i[0] for i in list(self.request.user.favouriteproperty_set.values_list('name'))]
        return favourite

    def getResponse(self):
        """
        This function implements logic for displaying the index page.

        :return: The render of the search results.
        """
        context = {
            'keyword': self.keyword,
            'res': self.search(),
            'district': self.district,
            'favourite': self.favourite(),
        }
        return render(self.request, "search/index.html", context)

    def favouriteResponse(self):
        """
        This function implements logic for toggling the favourites button.

        :return: Redirect back to the search page.
        """
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
