from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("films/", views.film_list, name="film_list"),
    path("books/", views.book_list, name="book_list"),
    path("films/<slug:slug>/", views.film_detail, name="film_detail"),
    path("books/<slug:slug>/", views.book_detail, name="book_detail"),
]
