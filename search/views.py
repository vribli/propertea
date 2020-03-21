from django.shortcuts import render
from django.http import HttpResponse
import requests

# Create your views here.
def index(request):
    try:
        keyword = request.GET['keyword']
        sortby = request.GET['sortby']
        filterby = request.GET['filterby']


        res = requests.get("https://developers.onemap.sg/commonapi/search?returnGeom=Y&getAddrDetails=Y&pageNum=1", params = {'searchVal' : keyword}).json()

        restest = [i for i in res.get('results') if not (i['POSTAL'] == 'NIL')]

        if sortby == "mostrelevant":
            pass
        elif sortby == "lowestprice":
            pass
        elif sortby == "smallestsize":
            pass


        if filterby == "public":
            pass
        elif filterby == "publicprivate":
            pass
        elif filterby == "private":
            pass
        else:
            pass

        context = {
            'keyword' : keyword,
            'res' : restest
        }
        return render(request, "search/index.html", context)
    except KeyError:
        return HttpResponse("Access through home, please")

