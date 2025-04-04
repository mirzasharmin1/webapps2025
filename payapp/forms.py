from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML


class AdminCreationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row mb-3'
            ),
            'username',
            'email',
            Row(
                Column('password', css_class='form-group col-md-6 mb-0'),
                Column('confirm_password', css_class='form-group col-md-6 mb-0'),
                css_class='form-row mb-3'
            ),
            Div(
                HTML(
                    '<a href="{% url \'payapp:admin_user_accounts\' %}" class="btn btn-secondary me-2"><i class="fas '
                    'fa-times me-1"></i> Cancel</a>'),
                Submit('submit', 'Create Administrator', css_class='btn-primary'),
                css_class='d-flex justify-content-end'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        username = cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(f"Username '{username}' is already taken")

        return cleaned_data
