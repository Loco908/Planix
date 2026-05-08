from django import forms
from .models import UserStory

class UserStoryForm(forms.ModelForm):
    class Meta:
        model = UserStory
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Como usuario quiero...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Criterios de aceptación y detalles...'}),
        }
