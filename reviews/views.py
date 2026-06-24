from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from content.models import Film, Book
from .forms import ReviewForm, CommentForm
from .models import Review, Comment, Like


@login_required
def new_review(request):
    """Landing page to pick a film or book before writing a review."""
    media_type = request.GET.get("type", "film")
    return render(request, "reviews/new_review.html", {"media_type": media_type})


@login_required
def write_review(request, work_type, slug):
    """Write or edit a review for a film or book."""
    if work_type == "film":
        work = get_object_or_404(Film, slug=slug)
        existing = Review.objects.filter(author=request.user, film=work).first()
    else:
        work = get_object_or_404(Book, slug=slug)
        existing = Review.objects.filter(author=request.user, book=work).first()

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=existing)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            if work_type == "film":
                review.film = work
                review.book = None
            else:
                review.book = work
                review.film = None
            review.save()
            return redirect(work.get_absolute_url())
    else:
        form = ReviewForm(instance=existing)

    return render(request, "reviews/write_review.html", {
        "form": form,
        "work": work,
        "work_type": work_type,
        "existing": existing,
    })


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, author=request.user)
    work_url = review.get_work_url()
    review.delete()
    return redirect(work_url)


@login_required
def add_comment(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.review = review
            comment.author = request.user
            comment.save()
    comments = review.comment_set.select_related("author").all()
    return render(request, "reviews/partials/comments.html", {
        "review": review,
        "comments": comments,
        "comment_form": CommentForm(),
    })


@login_required
def load_comments(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    comments = review.comment_set.select_related("author").all()
    return render(request, "reviews/partials/comments.html", {
        "review": review,
        "comments": comments,
        "comment_form": CommentForm(),
    })


@login_required
@require_POST
def toggle_like(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    like, created = Like.objects.get_or_create(review=review, user=request.user)
    if not created:
        like.delete()
    liked = created
    count = review.like_set.count()
    return render(request, "reviews/partials/like_button.html", {
        "review": review,
        "liked": liked,
        "like_count": count,
    })


@login_required
def search_tmdb(request):
    """HTMX: return film suggestions from TMDB."""
    from django.conf import settings
    import requests as http

    query = request.GET.get("q", "").strip()
    results = []
    if len(query) >= 2 and settings.TMDB_API_KEY:
        url = "https://api.themoviedb.org/3/search/movie"
        resp = http.get(url, params={"api_key": settings.TMDB_API_KEY, "query": query, "language": settings.TMDB_LANGUAGE}, timeout=5)
        if resp.ok:
            for item in resp.json().get("results", [])[:8]:
                results.append({
                    "tmdb_id": item["id"],
                    "title": item["title"],
                    "year": (item.get("release_date") or "")[:4],
                    "poster": f"https://image.tmdb.org/t/p/w92{item['poster_path']}" if item.get("poster_path") else "",
                })
    return render(request, "reviews/partials/tmdb_results.html", {"results": results, "query": query})


@login_required
def search_books(request):
    """HTMX: return book suggestions from Google Books."""
    import requests as http

    query = request.GET.get("q", "").strip()
    results = []
    if len(query) >= 2:
        from django.conf import settings
        params = {"q": query, "maxResults": 8, "printType": "books"}
        if settings.GOOGLE_BOOKS_API_KEY:
            params["key"] = settings.GOOGLE_BOOKS_API_KEY
        resp = http.get(
            "https://www.googleapis.com/books/v1/volumes",
            params=params,
            timeout=5,
        )
        if resp.ok:
            for item in resp.json().get("items", []):
                info = item.get("volumeInfo", {})
                identifiers = info.get("industryIdentifiers", [])
                isbn = next((x["identifier"] for x in identifiers if x["type"] == "ISBN_13"), "")
                cover = info.get("imageLinks", {}).get("thumbnail", "").replace("http://", "https://")
                results.append({
                    "title": info.get("title", ""),
                    "author": ", ".join(info.get("authors", [])),
                    "year": (info.get("publishedDate") or "")[:4] or None,
                    "isbn": isbn,
                    "cover": cover,
                })
    return render(request, "reviews/partials/book_results.html", {"results": results, "query": query})


@login_required
def select_tmdb_film(request):
    """Create/get a Film from a TMDB selection and redirect to the write-review page."""
    import requests as http
    from django.conf import settings

    tmdb_id = request.GET.get("tmdb_id")
    if not tmdb_id:
        return redirect("/reviews/new/?type=film")

    film = Film.objects.filter(tmdb_id=tmdb_id).first()
    if not film:
        resp = http.get(
            f"https://api.themoviedb.org/3/movie/{tmdb_id}",
            params={"api_key": settings.TMDB_API_KEY, "language": settings.TMDB_LANGUAGE, "append_to_response": "credits"},
            timeout=5,
        )
        if resp.ok:
            data = resp.json()
            film = Film.objects.create(
                title=data["title"],
                year=(data.get("release_date") or "")[:4] or None,
                director=", ".join(
                    c["name"] for c in data.get("credits", {}).get("crew", []) if c["job"] == "Director"
                ) if "credits" in data else "",
                poster_url=f"https://image.tmdb.org/t/p/w342{data['poster_path']}" if data.get("poster_path") else "",
                synopsis=data.get("overview", ""),
                tmdb_id=data["id"],
            )
        else:
            return redirect("/reviews/new/?type=film")

    return redirect(f"/reviews/film/{film.slug}/")


@login_required
def select_book(request):
    """Create/get a Book from an OpenLibrary selection and redirect to the write-review page."""
    title = request.GET.get("title", "").strip()
    author = request.GET.get("author", "").strip()
    year = request.GET.get("year", "").strip() or None
    isbn = request.GET.get("isbn", "").strip()
    cover = request.GET.get("cover", "").strip()

    if not title:
        return redirect("/reviews/new/?type=book")

    book = Book.objects.filter(isbn=isbn).first() if isbn else None
    if not book:
        book = Book.objects.create(
            title=title,
            author=author,
            year=year or None,
            isbn=isbn,
            cover_url=cover,
        )
    return redirect(f"/reviews/book/{book.slug}/")
