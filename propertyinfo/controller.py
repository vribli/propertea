import requests
from .models import MRTLRTData, BusData, PropertyImages

class PropertyInfoController:
    def __init__(self, request):
        self.name = request.GET['name']
        self.postal = request.GET['postal']
        # may break when user clicks on property from favourites list
        self.URL = "https://developers.onemap.sg/commonapi/search?searchVal={} {}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(self.name, self.postal)
        self.info = requests.get(self.URL).json()
        self.X = float(self.info['results'][0]['X'])
        self.Y = float(self.info['results'][0]['Y'])
        self.LAT = float(self.info['results'][0]['LATITUDE'])
        self.LONG = float(self.info['results'][0]['LONGITUDE'])
        self.MRT_LRT_Data = MRTLRTData(self.X, self.Y)
        self.Bus_Data = BusData(self.X, self.Y)
        self.images = PropertyImages(self.name)

    def getMRTLRTData(self):
        return self.MRT_LRT_Data

    def getBusData(self):
        return self.Bus_Data

    def getImages(self):
        return self.images.getLinks()

    def getImageURL(self):
        return self.images.getURL()
