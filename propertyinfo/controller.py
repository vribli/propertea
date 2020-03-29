import requests
from bs4 import BeautifulSoup
from . import models

class PropertyInfoController:
    def __init__(self, request):
        self.name = request.GET['name']
        self.postal = request.GET['postal']
        self.URL = "https://developers.onemap.sg/commonapi/search?searchVal={} {}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(self.name, self.postal)
        self.info = requests.get(self.URL).json()
        self.X = float(self.info['results'][0]['X'])
        self.Y = float(self.info['results'][0]['Y'])
        self.LAT = float(self.info['results'][0]['LATITUDE'])
        self.LONG = float(self.info['results'][0]['LONGITUDE'])
        self.MRT_LRT_Data = models.MRTLRTData(self.X, self.Y)
        self.Bus_Data = models.BusData(self.X, self.Y)

    def PropertyImages(self):
        url = 'https://www.google.no/search?client=opera&hs=cTQ&source=lnms&tbm=isch&sa=X&ved=0ahUKEwig3LOx4PzKAhWGFywKHZyZAAgQ_AUIBygB&biw=1920&bih=982'
        page = requests.get(url, params={'q': self.name + " singapore property"}).text

        soup = BeautifulSoup(page, 'html.parser')

        links = []

        for raw_img in soup.find_all('img'):
            link = raw_img.get('src')
            if link and 'http://' in link:
                links.append(link)
            if len(links) >= 3:
                break

        return links




