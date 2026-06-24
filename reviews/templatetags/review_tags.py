from django import template

register = template.Library()


@register.filter
def user_liked(review, user):
    if not user.is_authenticated:
        return False
    return review.like_set.filter(user=user).exists()
