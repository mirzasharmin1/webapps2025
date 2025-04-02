from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from .models import Account


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    currency = forms.ChoiceField(choices=Account.CURRENCY_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'currency')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'px-4 py-3'

        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'username',
            'email',
            'currency',
            HTML('<div class="form-text mb-3">You\'ll receive 750 GBP equivalent in your chosen currency.</div>'),
            'password1',
            'password2',
            Div(
                Submit('submit', 'Create Account', css_class='btn btn-primary btn-lg w-100 mt-3'),
                css_class='d-grid'
            )
        )


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'px-4 py-3'

        self.helper.layout = Layout(
            'username',
            'password',
            Div(
                Submit('submit', 'Log In', css_class='btn btn-primary btn-lg w-100 mt-2'),
                css_class='d-grid'
            ),
            HTML('<div class="text-center mt-3"><a href="#" class="text-decoration-none">Forgot password?</a></div>')
        )
