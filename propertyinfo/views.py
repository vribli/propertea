from bs4 import BeautifulSoup
from django.shortcuts import render
import requests 

# Create your views here.
def index(request):
    try:
        name = request.GET['name']
        postal = request.GET['postal']
        
        r = requests.get("https://www.squarefoot.com.sg/trends-and-analysis/residential?p={name_formatted}".format(name_formatted = name.replace(" ", "-"))) 

        info_raw = BeautifulSoup(r.content).find('table',{"class":"minimalist", "width":"95%"}).text.replace("\n\n", "").replace("#", "").replace("*", "").split("\n")
        info_heading = list(x for x in info_raw if info_raw.index(x) % 2 == 0)
        info_content = list(x for x in info_raw if info_raw.index(x) % 2 == 1)
        info_dict = dict(zip(info_heading, info_content))

        print(info_dict)
        context = {
            'name' : name,
            'postal' : postal,
            'info_dict' : info_dict
        }

        return render(request, "propertyinfo/index.html", context)
    except KeyError:
        return HttpResponse("Access through home, please")
