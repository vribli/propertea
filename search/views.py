from django.shortcuts import render
from django.http import HttpResponse
import requests

# Create your views here.
def index(request):
    try:
        keyword = request.GET['keyword']
        res = requests.get("https://developers.onemap.sg/commonapi/search?returnGeom=Y&getAddrDetails=Y&pageNum=1", params = {'searchVal' : keyword}).json()
        context = {
            'keyword' : keyword,
            'res' : res['results']
        }
        return render(request, "search/index.html", context)
    except KeyError:
        return HttpResponse("Access through home, please")

