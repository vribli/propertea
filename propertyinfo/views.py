from .controller import PropertyInfoController


# Create your views here.
def index(request):
    """
    This function displays the 'index' page.

    :param request: The HTTP request at that instance.
    :return: A HTTP response about the property information.
    """
    c = PropertyInfoController(request)
    return c.getResponse()
