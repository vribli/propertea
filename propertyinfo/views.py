from django.shortcuts import render

# Create your views here.
# Create your views here.
def index(request):
    try:
        name = request.GET['name']
        postal = request.GET['postal']

        // your code here

        context = {
            'name' : name,
            'postal' : postal
        }


        return render(request, "propertyinfo/index.html", context)
    except KeyError:
        return HttpResponse("Access through home, please")
