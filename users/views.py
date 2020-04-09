from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .controller import LoginController


@login_required(login_url='/users/login')
def index(request):
    """
    The function serves to access the 'users' page.

    :param request: HTTP Request of the Application
    :return: HTTP Response of LoginController relevant to the functionality.
    """
    c = LoginController(request)
    return c.indexResponse()


def login_view(request):
    """
    The function serves to access login functionality.

    :param request: HTTP Request of the Application
    :return: HTTP Response of LoginController relevant to the functionality.
    """
    c = LoginController(request)
    return c.loginResponse()


def logout_view(request):
    """
    The function serves to access logout functionality.

    :param request: HTTP Request of the Application
    :return: HTTP Response of LoginController relevant to the functionality.
    """
    c = LoginController(request)
    return c.logoutResponse()


def createaccount_view(request):
    """
    The function serves to access create account functionality.

    :param request: HTTP Request of the Application
    :return: HTTP Response of LoginController relevant to the functionality.
    """
    c = LoginController(request)
    return c.createAccountResponse()


def activate(request, uidb64, token):
    """
    This function serves to access account activation functionality.

    :param request: HTTP Request of the Application
    :param uidb64: Unique Slug generated from a combination of factors
    :param token: Token generated from a combination of factors
    :return: HTTP Response of LoginController relevant to the functionality.
    """
    c = LoginController(request)
    return c.activateResponse(uidb64, token)


def activation_sent_view(request):
    """
    This function serves to view the account activation page.

    :param request: HTTP Request of the Application
    :return: HTTP Response of LoginController relevant to the functionality.
    """
    c = LoginController(request)
    return c.activationSentResponse()


def redirect_view(request):
    """
    This function serves to view the redirect success page.

    :param request: HTTP Request of the Application
    :return: HTTP Response of LoginController relevant to the functionality.
    """
    return redirect('/redirect-success/')
