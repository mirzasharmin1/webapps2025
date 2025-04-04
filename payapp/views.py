from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect

from payapp.forms import AdminCreationForm
from register.models import Account


def home(request):
    """Home page view - redirects admins to admin dashboard"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('payapp:admin_dashboard')
        return render(request, 'home.html')
    return render(request, 'home.html')


@login_required
def send_money_placeholder(request):
    """Placeholder for send money feature"""
    return render(request, 'money/send_money.html')


@login_required
def request_money_placeholder(request):
    """Placeholder for request money feature"""
    return render(request, 'money/request_money.html')


@login_required
def transactions_placeholder(request):
    """Placeholder for transactions history"""
    return render(request, 'money/transactions.html')


@login_required
def profile_placeholder(request):
    """Placeholder for user profile"""
    return render(request, 'profile.html')


@login_required
def notifications_placeholder(request):
    """Placeholder for notifications"""
    return render(request, 'notifications.html')


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view"""
    total_users = User.objects.count()
    admin_users = User.objects.filter(is_staff=True).count()
    regular_users = total_users - admin_users

    context = {
        'total_users': total_users,
        'admin_users': admin_users,
        'regular_users': regular_users
    }

    return render(request, 'payapp_admin/dashboard.html', context)


@user_passes_test(is_admin)
def admin_user_accounts(request):
    """View all user accounts"""
    accounts = Account.get_all_accounts()

    context = {
        'accounts': accounts
    }

    return render(request, 'payapp_admin/user_accounts.html', context)


@user_passes_test(is_admin)
def admin_toggle_staff_status(request, user_id):
    """Toggle staff status of a user"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        if user == request.user:
            messages.error(request, "You cannot remove your own admin status")
            return redirect('payapp:admin_user_accounts')

        # Toggle the status
        user.is_staff = not user.is_staff
        user.save()

        status = "administrator" if user.is_staff else "regular user"
        messages.success(request, f"{user.username} is now a {status}")

    return redirect('payapp:admin_user_accounts')


@user_passes_test(is_admin)
def admin_create_admin(request):
    """Create a new admin user"""
    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    is_staff=True  # Make them staff/admin
                )

                messages.success(request, f"Administrator {user.username} has been created successfully")
                return redirect('payapp:admin_user_accounts')
    else:
        form = AdminCreationForm()

    return render(request, 'payapp_admin/create_admin.html', {'form': form})
