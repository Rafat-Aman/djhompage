# core/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse
from .forms import SignUpForm
# core/views.py (only the dashboard import and view changed)
from allauth.socialaccount.models import SocialAccount
from .google_api import get_storage_quota, GoogleAPIError

def home(request):
    return render(request, "home.html", {"title": "Welcome"})

def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()  # creates the user
            messages.success(request, "Your account was created. You can sign in now.")
            return redirect("account_login")  # allauth login
        messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def profile(request):
    return render(request, "profile.html")

@login_required
def dashboard(request):
    # List all Google accounts linked to this user
    google_accounts = SocialAccount.objects.filter(user=request.user, provider="google")
    return render(request, "dashboard.html", {"google_accounts": google_accounts})

@login_required
def disconnect_google(request, pk: int):
    # Remove a linked Google account (and its stored tokens)
    sa = get_object_or_404(SocialAccount, pk=pk, user=request.user, provider="google")
    if request.method == "POST":
        sa.delete()
        messages.success(request, "Disconnected Google account.")
        return redirect("dashboard")
    # For safety, only allow POST
    messages.error(request, "Invalid request.")
    return redirect("dashboard")
@login_required
def dashboard(request):
    google_accounts = SocialAccount.objects.filter(user=request.user, provider="google")
    items = []
    for acc in google_accounts:
        quota = None
        error = None
        try:
            quota = get_storage_quota(acc)
        except GoogleAPIError as e:
            error = str(e)
        except Exception as e:
            error = f"Unexpected error: {e}"
        items.append({"account": acc, "quota": quota, "error": error})

    return render(request, "dashboard.html", {"items": items})