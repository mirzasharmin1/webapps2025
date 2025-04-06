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


class SendMoneyForm(forms.Form):
    recipient_email = forms.EmailField(label="Recipient's Email")
    amount = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2, label="Amount")
    description = forms.CharField(max_length=255, required=False, label="Description (optional)")

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'recipient_email',
            'amount',
            'description',
            Div(
                Submit('submit', 'Send Money', css_class='btn-primary'),
                css_class='d-grid gap-2 col-6 mx-auto mt-4'
            )
        )

    def clean_recipient_email(self):
        email = self.cleaned_data['recipient_email']
        try:
            recipient = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("No user with this email address exists.")

        if self.sender and recipient == self.sender:
            raise forms.ValidationError("You cannot send money to yourself.")

        return email

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if self.sender and hasattr(self.sender, 'account'):
            if amount > self.sender.account.balance:
                raise forms.ValidationError(
                    f"Insufficient funds. Your current balance is {self.sender.account.balance} {self.sender.account.currency}.")

        return amount


class RequestMoneyForm(forms.Form):
    sender_email = forms.EmailField(label="Request From (Email)")
    amount = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2, label="Amount")
    description = forms.CharField(max_length=255, required=False, label="Description (optional)")

    def __init__(self, *args, **kwargs):
        self.requester = kwargs.pop('requester', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'sender_email',
            'amount',
            'description',
            Div(
                Submit('submit', 'Request Money', css_class='btn-primary'),
                css_class='d-grid gap-2 col-6 mx-auto mt-4'
            )
        )

    def clean_sender_email(self):
        email = self.cleaned_data['sender_email']
        try:
            sender = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError("No user with this email address exists.")

        if self.requester and sender == self.requester:
            raise forms.ValidationError("You cannot request money from yourself.")

        return email


class PaymentRequestResponseForm(forms.Form):
    CHOICES = [
        ('accept', 'Accept and Pay'),
        ('reject', 'Reject Request')
    ]

    action = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        self.responder = kwargs.pop('responder', None)
        self.transaction = kwargs.pop('transaction', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            'action',
            Div(
                Submit('submit', 'Submit Response', css_class='btn-primary'),
                css_class='d-grid gap-2 col-6 mx-auto mt-4'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')

        if action == 'accept' and self.responder and self.transaction:
            if self.transaction.amount > self.responder.account.balance:
                raise forms.ValidationError(
                    f"Insufficient funds to accept this payment request. Your current balance is {self.responder.account.balance} {self.responder.account.currency}.")

        return cleaned_data


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            # Pre-populate the form with the user's current data
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row mb-3'
            ),
            'email',
            Div(
                Submit('submit', 'Update Profile', css_class='btn-primary'),
                css_class='d-grid gap-2 col-6 mx-auto mt-4'
            )
        )

    def clean_email(self):
        email = self.cleaned_data['email']

        # Check if the email already exists for another user
        if User.objects.exclude(pk=self.user.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already registered to another user.")

        return email
