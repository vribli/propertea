from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .controller import LoginController


@login_required(login_url='/users/login')
def index(request):
    c = LoginController(request)
    return c.indexResponse()


def login_view(request):
    c = LoginController(request)
    return c.loginResponse()


def logout_view(request):
    c = LoginController(request)
    return c.logoutResponse()


def createaccount_view(request):
    c = LoginController(request)
    return c.createAccountResponse()


def activate(request, uidb64, token):
    c = LoginController(request)
    return c.activateResponse(uidb64, token)


def activation_sent_view(request):
    c = LoginController(request)
    return c.activationSentResponse()


def redirect_view(request):
    return redirect('/redirect-success/')
