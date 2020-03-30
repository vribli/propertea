from .controller import PropertyInfoController


# Create your views here.
def index(request):
    c = PropertyInfoController(request)
    return c.getResponse()
