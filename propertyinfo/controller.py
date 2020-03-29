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
        self.images = models.PropertyImages(self.name)

    def getMRTLRTData(self):
        return self.MRT_LRT_Data

    def getBusData(self):
        return self.Bus_Data

    def getImages(self):
        return self.images.getLinks()

    def getImageURL(self):
        return self.images.getURL()
