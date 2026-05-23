from django import forms
from django.forms.models import inlineformset_factory
from .models import UserStory, UserStoryTask, AcceptanceCriterion

class UserStoryForm(forms.ModelForm):
    class Meta:
        model = UserStory
        fields = ['title', 'description', 'status', 'value', 'effort']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Como usuario quiero...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción detallada...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.Select(attrs={'class': 'form-select'}),
            'effort': forms.Select(attrs={'class': 'form-select'}),
        }

class UserStoryTaskForm(forms.ModelForm):
    class Meta:
        model = UserStoryTask
        fields = ['description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nueva tarea'}),
        }

class AcceptanceCriterionForm(forms.ModelForm):
    class Meta:
        model = AcceptanceCriterion
        fields = ['description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nuevo criterio de aceptación'}),
        }

UserStoryTaskFormSet = inlineformset_factory(
    UserStory, UserStoryTask,
    form=UserStoryTaskForm,
    extra=1,
    can_delete=True
)

AcceptanceCriterionFormSet = inlineformset_factory(
    UserStory, AcceptanceCriterion,
    form=AcceptanceCriterionForm,
    extra=1,
    can_delete=True
)
