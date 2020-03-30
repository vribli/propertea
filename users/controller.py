from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.defaultfilters import striptags
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import SignUpForm
from .models import User
from .tokens import account_activation_token


class LoginController():
    def __init__(self, request):
        self.request = request

    def login(self):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect("/users")
        elif self.request.POST:
            username = self.request.POST["username"]
            password = self.request.POST["password"]
            user = authenticate(self.request, username=username, password=password)
            if user is not None:
                login(self.request, user)
                next_url = self.request.POST.get('next_url')
                if next_url is None:
                    return HttpResponseRedirect("/")
                if next_url != "/users/login":
                    return HttpResponseRedirect(next_url)
                else:
                    context = {
                        "user": self.request.user,
                        "favourites": [i[0] for i in list(self.request.user.favouriteproperty_set.values_list('name'))]
                    }
                    return HttpResponseRedirect("/users")
            else:
                messages.error(self.request, "Invalid Credentials")
                return render(self.request, "users/login.html")
        else:
            return render(self.request, "users/login.html")
