from django.urls import path
from . import views

urlpatterns = [
    path("reviews/new/", views.new_review, name="new_review"),
    path("reviews/search/films/", views.search_tmdb, name="search_tmdb"),
    path("reviews/search/books/", views.search_books, name="search_books"),
    path("reviews/select/film/", views.select_tmdb_film, name="select_tmdb_film"),
    path("reviews/select/book/", views.select_book, name="select_book"),
    path("reviews/<int:review_id>/comments/", views.load_comments, name="load_comments"),
    path("reviews/<int:review_id>/comments/add/", views.add_comment, name="add_comment"),
    path("reviews/<int:review_id>/like/", views.toggle_like, name="toggle_like"),
    path("reviews/<int:pk>/delete/", views.delete_review, name="delete_review"),
    path("reviews/<str:work_type>/<slug:slug>/", views.write_review, name="write_review"),
]
