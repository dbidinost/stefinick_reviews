from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.shortcuts import render, get_object_or_404

from .models import Film, Book
from reviews.models import Review


@login_required
def home(request):
    # Recently reviewed films (with at least 1 review)
    recent_films = (
        Film.objects.annotate(review_count=Count("review"), avg_rating=Avg("review__rating"))
        .filter(review_count__gt=0)
        .order_by("-added_at")[:8]
    )
    recent_books = (
        Book.objects.annotate(review_count=Count("review"), avg_rating=Avg("review__rating"))
        .filter(review_count__gt=0)
        .order_by("-added_at")[:8]
    )
    return render(request, "content/home.html", {
        "recent_films": recent_films,
        "recent_books": recent_books,
    })


@login_required
def film_list(request):
    films = (
        Film.objects.annotate(review_count=Count("review"), avg_rating=Avg("review__rating"))
        .order_by("title")
    )
    return render(request, "content/film_list.html", {"films": films})


@login_required
def book_list(request):
    books = (
        Book.objects.annotate(review_count=Count("review"), avg_rating=Avg("review__rating"))
        .order_by("title")
    )
    return render(request, "content/book_list.html", {"books": books})


@login_required
def film_detail(request, slug):
    film = get_object_or_404(Film, slug=slug)
    reviews = (
        film.review_set.select_related("author")
        .prefetch_related("comment_set__author", "like_set")
        .order_by("-created_at")
    )
    avg = reviews.aggregate(a=Avg("rating"))["a"]
    user_review = reviews.filter(author=request.user).first()
    return render(request, "content/film_detail.html", {
        "work": film,
        "work_type": "film",
        "reviews": reviews,
        "avg_rating": avg,
        "user_review": user_review,
    })


@login_required
def book_detail(request, slug):
    book = get_object_or_404(Book, slug=slug)
    reviews = (
        book.review_set.select_related("author")
        .prefetch_related("comment_set__author", "like_set")
        .order_by("-created_at")
    )
    avg = reviews.aggregate(a=Avg("rating"))["a"]
    user_review = reviews.filter(author=request.user).first()
    return render(request, "content/book_detail.html", {
        "work": book,
        "work_type": "book",
        "reviews": reviews,
        "avg_rating": avg,
        "user_review": user_review,
    })
