from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import InviteRegistrationForm, ProfileEditForm
from .models import User


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"


def register(request):
    if request.method == "POST":
        form = InviteRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = InviteRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("/accounts/login/")


def profile(request, username):
    member = get_object_or_404(User, username=username)
    user_reviews = member.review_set.select_related("film", "book").order_by("-created_at")
    return render(request, "accounts/profile.html", {"member": member, "user_reviews": user_reviews})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(f"/accounts/profile/{request.user.username}/")
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "accounts/edit_profile.html", {"form": form})
