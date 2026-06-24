from django.conf import settings
from django.db import models


RATING_CHOICES = [(i, str(i)) for i in range(1, 11)]

HALF_STARS = {
    1: "½",
    2: "★",
    3: "★½",
    4: "★★",
    5: "★★½",
    6: "★★★",
    7: "★★★½",
    8: "★★★★",
    9: "★★★★½",
    10: "★★★★★",
}


class Review(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    film = models.ForeignKey("content.Film", on_delete=models.CASCADE, null=True, blank=True)
    book = models.ForeignKey("content.Book", on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["author", "film"], condition=models.Q(film__isnull=False), name="unique_user_film_review"),
            models.UniqueConstraint(fields=["author", "book"], condition=models.Q(book__isnull=False), name="unique_user_book_review"),
            models.CheckConstraint(
                condition=(models.Q(film__isnull=False) & models.Q(book__isnull=True)) |
                          (models.Q(film__isnull=True) & models.Q(book__isnull=False)),
                name="review_has_exactly_one_work",
            ),
        ]

    def __str__(self):
        work = self.film or self.book
        return f"{self.author} on {work}"

    @property
    def rating_display(self):
        return HALF_STARS.get(self.rating, str(self.rating))

    def get_work(self):
        return self.film or self.book

    def get_work_url(self):
        work = self.get_work()
        return work.get_absolute_url() if work else "#"

    def like_count(self):
        return self.like_set.count()

    def user_has_liked(self, user):
        return self.like_set.filter(user=user).exists()


class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author} on review #{self.review_id}"


class Like(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["review", "user"], name="unique_like_per_user")
        ]
