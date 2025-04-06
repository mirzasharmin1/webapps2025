from decimal import Decimal

import requests
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from payapp.forms import AdminCreationForm, SendMoneyForm, RequestMoneyForm, PaymentRequestResponseForm, ProfileForm
from payapp.models import Transaction, Notification
from register.models import Account
from register.views import get_conversion_rate


def home(request):
    """Home page view - redirects admins to admin dashboard"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('payapp:admin_dashboard')
        return render(request, 'home.html')
    return render(request, 'home.html')


@login_required
def send_money(request):
    if request.method == 'POST':
        form = SendMoneyForm(request.POST, sender=request.user)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            recipient = User.objects.get(email=recipient_email)

            with transaction.atomic():
                sender_currency = request.user.account.currency
                recipient_currency = recipient.account.currency

                if sender_currency != recipient_currency:
                    conversion_rate = get_conversion_rate(sender_currency, recipient_currency)
                    recipient_amount = amount * conversion_rate
                else:
                    recipient_amount = amount

                request.user.account.balance -= amount
                request.user.account.save()

                recipient.account.balance += recipient_amount
                recipient.account.save()

                Transaction.objects.create(
                    sender=request.user,
                    recipient=recipient,
                    amount=amount,
                    sender_currency=sender_currency,
                    recipient_currency=recipient_currency,
                    transaction_type='PAYMENT',
                    status='COMPLETED',
                    description=description
                )

            messages.success(request, f"Successfully sent {amount} {sender_currency} to {recipient.username}")
            return redirect('payapp:transactions')
    else:
        form = SendMoneyForm(sender=request.user)

    return render(request, 'money/send_money.html', {'form': form})


@login_required
def request_money(request):
    if request.method == 'POST':
        form = RequestMoneyForm(request.POST, requester=request.user)
        if form.is_valid():
            sender_email = form.cleaned_data['sender_email']
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']

            sender = User.objects.get(email=sender_email)

            Transaction.objects.create(
                sender=request.user,
                recipient=sender,
                amount=amount,
                sender_currency=request.user.account.currency,
                recipient_currency=sender.account.currency,
                transaction_type='REQUEST',
                status='PENDING',
                description=description
            )

            messages.success(request,
                             f"Payment request for {amount} {request.user.account.currency} sent to {sender.username}")
            return redirect('payapp:transactions')
    else:
        form = RequestMoneyForm(requester=request.user)

    return render(request, 'money/request_money.html', {'form': form})


@login_required
def transactions(request):
    user_transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-timestamp')

    context = {
        'transactions': user_transactions
    }

    return render(request, 'money/transactions.html', context)


@login_required
def transaction_detail(request, transaction_id):
    current_transaction = get_object_or_404(
        Transaction,
        id=transaction_id
    )

    Notification.objects.filter(
        user=request.user,
        transaction=current_transaction,
        is_read=False
    ).update(is_read=True)

    show_response_form = (
            current_transaction.transaction_type == 'REQUEST' and
            current_transaction.recipient == request.user and
            current_transaction.status == 'PENDING'
    )

    response_form = None
    if show_response_form:
        if request.method == 'POST':
            response_form = PaymentRequestResponseForm(
                request.POST,
                responder=request.user,
                transaction=current_transaction
            )

            if response_form.is_valid():
                action = response_form.cleaned_data['action']

                with transaction.atomic():
                    if action == 'accept':
                        payer_currency = request.user.account.currency
                        payee_currency = current_transaction.sender.account.currency
                        amount = current_transaction.amount

                        if payer_currency != payee_currency:
                            conversion_rate = get_conversion_rate(payer_currency, payee_currency)
                            payee_amount = amount * conversion_rate
                        else:
                            payee_amount = amount

                        request.user.account.balance -= amount
                        request.user.account.save()

                        current_transaction.sender.account.balance += payee_amount
                        current_transaction.sender.account.save()

                        current_transaction.status = 'COMPLETED'
                        current_transaction.save()

                        messages.success(request, f"Payment of {amount} {payer_currency} successfully sent")
                    else:  # reject
                        current_transaction.status = 'REJECTED'
                        current_transaction.save()
                        messages.info(request, "Payment request rejected")

                return redirect('payapp:transactions')
        else:
            response_form = PaymentRequestResponseForm(
                responder=request.user,
                transaction=current_transaction
            )

    context = {
        'transaction': current_transaction,
        'show_response_form': show_response_form,
        'response_form': response_form,
        'converted_amount': get_conversion_rate(
            current_transaction.sender_currency,
            current_transaction.recipient_currency,
            current_transaction.amount
        )
    }

    return render(request, 'money/transaction_detail.html', context)


@login_required
def notifications(request):
    # Get user's notifications
    user_notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')

    # Mark all as read when viewing
    unread_count = user_notifications.filter(is_read=False).count()
    if unread_count > 0:
        user_notifications.filter(is_read=False).update(is_read=True)

    context = {
        'notifications': user_notifications,
        'unread_count': unread_count
    }

    return render(request, 'notifications.html', context)


@login_required
def profile(request):
    sent_payments = Transaction.objects.filter(
        sender=request.user,
        transaction_type='PAYMENT',
        status='COMPLETED'
    ).count()

    received_payments = Transaction.objects.filter(
        recipient=request.user,
        transaction_type='PAYMENT',
        status='COMPLETED'
    ).count()

    sent_requests = Transaction.objects.filter(
        sender=request.user,
        transaction_type='REQUEST'
    ).count()

    received_requests = Transaction.objects.filter(
        recipient=request.user,
        transaction_type='REQUEST'
    ).count()

    if request.method == 'POST':
        form = ProfileForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            messages.success(request, "Your profile has been updated successfully.")
            return redirect('payapp:profile')
    else:
        form = ProfileForm(user=request.user)

    context = {
        'form': form,
        'sent_payments': sent_payments,
        'received_payments': received_payments,
        'sent_requests': sent_requests,
        'received_requests': received_requests
    }

    return render(request, 'profile.html', context)


def is_admin(user):
    return user.is_staff


@user_passes_test(is_admin)
def admin_dashboard(request):
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
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        if user == request.user:
            messages.error(request, "You cannot remove your own admin status")
            return redirect('payapp:admin_user_accounts')

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


@user_passes_test(is_admin)
def admin_transactions(request):
    all_transactions = Transaction.objects.all().order_by('-timestamp')

    context = {
        'transactions': all_transactions
    }

    return render(request, 'payapp_admin/transactions.html', context)
