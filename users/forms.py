from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=400)
    last_name = forms.CharField(max_length=400)
    email = forms.EmailField(max_length=400)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = mark_safe(
            'Your username should:'
            '<span class="fake-ul">'
            '<span class="fake-li">Be unique</span>'
            '<span class="fake-li">Have a maximum of 150 characters</span>'
        )
        self.fields['password1'].help_text = mark_safe(
            'Your password should:'
            '<span class="fake-ul">'
            '<span class="fake-li">Have at least 8 characters</span>'
            '<span class="fake-li">Not contain any personal information</span>'
            '<span class="fake-li">Not be entirely numeric</span>'
            '</span>'
        )
        self.fields['password2'].help_text = "Enter your password again for verification."
