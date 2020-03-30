import requests
from .models import MRTLRTData, BusData, PropertyImages
from django.shortcuts import render


class PropertyInfoController:
    """
    This controller class executes the logic for the 'PropertyInfo' sub-application.

    :ivar name: Name of property considered.
    :ivar keyword: Search keyword used to find the building.
    :ivar URL: URL for API.
    :ivar info: Information Retrieved from API.
    :ivar address: Address of Property.
    :ivar X: X-Coordinate of Property.
    :ivar Y: Y-Coordinate of Property.
    :ivar LAT: Latitude of Property.
    :ivar LONG: Longitude of Property.
    :ivar MRT_LRT_Data: Data of the nearest MRT/LRT.
    :ivar Bus_Data: Data of the nearest Bus Stop.
    :ivar images: Data from Google Images.
    :ivar request: The HTTP Request at that instance.
    """
    def __init__(self, request):
        self.name = request.GET['name']
        self.keyword = request.GET['keyword']
        # may break when user clicks on property from favourites list
        self.URL = "https://developers.onemap.sg/commonapi/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            self.name)
        self.info = [i for i in requests.get(self.URL).json().get('results') if not (i['POSTAL'] == 'NIL')]
        self.address = self.info[0]['ADDRESS']
        self.X = float(self.info[0]['X'])
        self.Y = float(self.info[0]['Y'])
        self.LAT = float(self.info[0]['LATITUDE'])
        self.LONG = float(self.info[0]['LONGITUDE'])
        self.MRT_LRT_Data = MRTLRTData(self.X, self.Y)
        self.Bus_Data = BusData(self.X, self.Y)
        self.images = PropertyImages(self.name)
        self.request = request

    def getResponse(self):
        """
        Returns the 'index' page for the propertyinfo sub-application.

        :return: Render of 'index' page.
        """
        context = {
            'name': self.name,
            'address': self.address,
            'mrt_lrt_plot': self.MRT_LRT_Data.plot(),
            'mrt_lrt_table_plot': self.MRT_LRT_Data.table(),
            'bus_plot': self.Bus_Data.plot(),
            'bus_table_plot': self.Bus_Data.table(),
            'links': self.images.getLinks(),
            'url': self.images.getURL(),
            'LAT': self.LAT,
            'LONG': self.LONG,
            'nearest_train_lat': self.MRT_LRT_Data.lat,
            'nearest_train_long': self.MRT_LRT_Data.long,
            'nearest_bus_lat': self.Bus_Data.lat,
            'nearest_bus_long': self.Bus_Data.long,
            'keyword': self.keyword,

        }
        return render(self.request, "propertyinfo/index.html", context)
