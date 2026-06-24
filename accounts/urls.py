from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
]
