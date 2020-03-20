from django.contrib.auth import authenticate, login, logout
from django.template.defaultfilters import striptags

from .models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import SignUpForm


# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return render(request, "users/login.html", {"message": None})
    context = {
        "user": request.user
    }
    return render(request, "users/user.html", context)


def login_view(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        messages.error(request, "Invalid Credentials")
        return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged Out.")
    return render(request, "users/login.html")


def createaccount_view(request):
    form = SignUpForm(request.POST)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        email = form.cleaned_data.get('email')
        user = authenticate(username=username, password=password)
        login(request, user)
        user = authenticate(username=username, password=password)
        print("User is authenticated:" + str(request.user.is_authenticated))
        login(request, user)
        return redirect(to="index")
    else:
        if striptags(form.errors) != "usernameThis field is required.emailThis field is required.first_nameThis field " \
                                     "is required.last_nameThis field is required.password1This field is " \
                                     "required.password2This field is required.":
            errorlist=[]
            for errors in form.errors.items():
                errorlist.append(errors[1][0])
            messages.error(request, errorlist)
            print(errorlist)
        form = SignUpForm()
    return render(request, 'users/createaccount.html', {'form': form})
