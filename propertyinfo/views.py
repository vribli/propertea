from .controller import PropertyInfoController
from django.shortcuts import render


# Create your views here.
def index(request):
    c = PropertyInfoController(request)

    context = {
        'name': c.name,
        'postal': c.postal,
        'mrt_lrt_plot': c.getMRTLRTData().plot(),
        'mrt_lrt_table_plot': c.getMRTLRTData().table(),
        'bus_plot': c.getBusData().plot(),
        'bus_table_plot': c.getBusData().table(),
        'links': c.getImages(),
        'url': c.getImageURL(),
        'LAT': c.LAT,
        'LONG': c.LONG,
        'nearest_train_lat': c.getMRTLRTData().lat,
        'nearest_train_long': c.getMRTLRTData().long,
        'nearest_bus_lat': c.getBusData().lat,
        'nearest_bus_long': c.getBusData().long
    }

    return render(request, "propertyinfo/index.html", context)
