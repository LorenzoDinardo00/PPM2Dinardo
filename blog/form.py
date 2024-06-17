from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ["post"]
        labels ={
            "user_name": "Scrivi il tuo nome",
            "user_email": "Scrivi la tua email",
            "text": "Scrivi il tuo commento qui"
        }

