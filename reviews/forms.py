from django import forms
from .models import Review, Comment, RATING_CHOICES


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "star-radio"}),
    )

    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {
            "text": forms.Textarea(attrs={"rows": 6, "placeholder": "What did you think?"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Aggiungi un commento…",
                "class": "w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-green-500",
            }),
        }
        labels = {"text": ""}
