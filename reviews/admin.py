from django.contrib import admin
from .models import Review, Comment, Like


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author", "film", "book", "rating", "created_at")
    list_filter = ("rating",)
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "review", "created_at")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("user", "review", "created_at")
