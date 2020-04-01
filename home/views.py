from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    """
    This function seeks to display the 'index' page of the Home sub-application.

    :param request: The HTTP request at that instance.
    :return: Render of the 'index' page.
    """
    return render(request, "home/index.html")


def bydistrict(request):
    """
    This function seeks to display the 'bydistrict' page of the Home sub-application.
    :param request: The HTTP Request at that instance.
    :return: Render of the "bydistrict' page.
    """
    return render(request, "home/bydistrict.html")
