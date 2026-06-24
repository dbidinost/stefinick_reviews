from django.contrib import admin
from .models import Film, Book


@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "director", "tmdb_id")
    search_fields = ("title", "director")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "year", "isbn")
    search_fields = ("title", "author")
    prepopulated_fields = {"slug": ("title",)}
