import decimal

import requests
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView, LogoutView as BaseLogoutView
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from webapps2025.settings import BASE_URL
from .forms import UserRegistrationForm, CustomLoginForm


def get_conversion_rate(from_currency, to_currency, amount=1):
    """Get conversion rate from REST service"""
    try:
        response = requests.get(f'{BASE_URL}/conversion/{from_currency}/{to_currency}/{amount}/')
        if response.status_code == 200:
            data = response.json()
            return decimal.Decimal(data['converted_amount'])
        return None
    except Exception as e:
        print(f"Error fetching conversion rate: {e}")
        return None


class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'register/register.html'
    success_url = reverse_lazy('auth:login')

    def form_valid(self, form):

        with transaction.atomic():
            response = super().form_valid(form)
            user = self.object

            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            currency = form.cleaned_data['currency']
            user.account.currency = currency

            initial_gbp = decimal.Decimal('750.00')

            if currency == 'GBP':
                initial_balance = initial_gbp
            else:
                conversion_rate = get_conversion_rate('GBP', currency)
                if conversion_rate:
                    initial_balance = initial_gbp * conversion_rate
                else:
                    messages.error(self.request, "Currency conversion failed. Please try again with a valid currency.")
                    return redirect('auth:register')

            user.account.balance = initial_balance
            user.account.save()

            # Log the user in
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(self.request, user)

            messages.success(self.request,
                             f'Account created successfully! Your initial balance is {initial_balance} {currency}.')
            return redirect('payapp:home')


class CustomLoginView(LoginView):
    template_name = 'register/login.html'
    form_class = CustomLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/webapps2025/')
        return super().dispatch(request, *args, **kwargs)


def custom_logout_view(request):
    logout(request)
    return redirect('/auth/login/')
