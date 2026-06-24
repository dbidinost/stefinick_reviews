from django.db import models
from django.utils.text import slugify


class Film(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    director = models.CharField(max_length=255, blank=True)
    poster_url = models.URLField(blank=True)
    synopsis = models.TextField(blank=True)
    tmdb_id = models.IntegerField(null=True, blank=True, unique=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.year})" if self.year else self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.title}-{self.year or ''}")
            self.slug = self._unique_slug(base)
        super().save(*args, **kwargs)

    def _unique_slug(self, base):
        slug = base
        n = 1
        while Film.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    @property
    def image_url(self):
        return self.poster_url

    def get_absolute_url(self):
        return f"/films/{self.slug}/"


class Book(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    author = models.CharField(max_length=255, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    cover_url = models.URLField(blank=True)
    synopsis = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.author})" if self.author else self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.title}-{self.author or ''}")
            self.slug = self._unique_slug(base)
        super().save(*args, **kwargs)

    def _unique_slug(self, base):
        slug = base
        n = 1
        while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        return slug

    @property
    def image_url(self):
        return self.cover_url

    def get_absolute_url(self):
        return f"/books/{self.slug}/"
