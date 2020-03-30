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

    def indexResponse(self):
        context = {
            "user": self.request.user,
            "favourites": [i[0] for i in list(self.request.user.favouriteproperty_set.values_list('name'))]
        }
        return render(self.request, "users/user.html", context)

    def loginResponse(self):
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

    def logoutResponse(self):
        logout(self.request)
        messages.success(self.request, "Logged Out.")
        return HttpResponseRedirect("/users/login")

    def createAccountResponse(self):
        form = SignUpForm(self.request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)

            # user can't login until link confirmed
            user.is_active = False
            user.save()
            # current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template()
            # and calls its render() method immediately.
            message = render_to_string('users/activation_request.html', {
                'user': user,
                'domain': "127.0.0.1:8000",
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect("activation_sent")
        else:
            if striptags(
                    form.errors) != "usernameThis field is required.emailThis field is required.first_nameThis field " \
                                    "is required.last_nameThis field is required.password1This field is " \
                                    "required.password2This field is required.":
                errorlist = []
                for errors in form.errors.items():
                    messages.error(self.request, errors[1][0])
                    print(errors)
            form = SignUpForm()
        return render(self.request, 'users/createaccount.html', {'form': form})

    def activateResponse(self, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        # checking if the user exists, if the token is valid.
        if user is not None and account_activation_token.check_token(user, token):
            # if valid set active true
            user.is_active = True
            # set signup_confirmation true
            user.profile.signup_confirmation = True
            user.save()
            login(self.request, user)
            return redirect('index')
        else:
            return render(self.request, 'users/activation_invalid.html')

    def activationSentResponse(self):
        return render(self.request, 'users/activation_sent.html')
