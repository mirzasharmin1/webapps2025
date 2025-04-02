from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def home(request):
    """Simple home page"""
    if request.user.is_authenticated:
        return HttpResponse(f"Welcome, {request.user.username}! You are logged in successfully.")
    else:
        return HttpResponse("Welcome to PayApp. Please log in or register.")


@login_required
def dashboard_placeholder(request):
    """Very simple dashboard placeholder"""
    return HttpResponse(f"Dashboard placeholder. Welcome {request.user.username}! Your balance: {request.user.account.balance} {request.user.account.currency}")
