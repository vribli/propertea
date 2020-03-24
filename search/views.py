from django.shortcuts import render
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from pandas import *


# Create your views here.
def index(request):
    if True:
        keyword = request.GET['keyword']
        filterby = request.GET['filterby']
        district = request.GET['district']

        if (keyword == 'nil') & (filterby == 'nil') & (district != 'nil'):
            xls = ExcelFile("propertea/static/propertea.xlsx")
            data = xls.parse(xls.sheet_names[0])
            data = data.to_dict('index')
            values = [v for v in data.values()]
            resfiltered = [i for i in values if (i['DISTRICT'] == district)]

        else:
            res = requests.get("https://developers.onemap.sg/commonapi/search?returnGeom=Y&getAddrDetails=Y&pageNum=1", params = {'searchVal' : keyword}).json()

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
                    info_raw = BeautifulSoup(r.content).find('table', {"class": "minimalist", "width": "95%"}).text.replace("\n\n", "").replace("#", "").replace("*", "").split("\n")
                    ptype = "Non-Landed Residential"
                except:
                    try:
                        r = requests.get(URLL)
                        info_raw = BeautifulSoup(r.content).find('table',{"class": "minimalist", "width": "95%"}).text.replace("\n\n", "").replace("#", "").replace("*", "").split("\n")
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
            'keyword' : keyword,
            'res' : resfiltered2,
            'district': district
        }
        return render(request, "search/index.html", context)
    #except KeyError:
    #    return HttpResponse("Access through home, please")

