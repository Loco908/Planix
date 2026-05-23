from django import forms
from django.forms.models import inlineformset_factory
from .models import UserStory, UserStoryTask, AcceptanceCriterion, Sprint, Ticket, TicketAcceptanceCriterion

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

class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['name', 'start_date', 'end_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Sprint'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        status = cleaned_data.get('status')

        if start_date and end_date and start_date > end_date:
            self.add_error('end_date', 'La fecha de fin debe ser posterior a la fecha de inicio.')
            
        return cleaned_data

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'user_story', 'title', 'description', 'type', 'value', 'status', 'effort', 
            'assigned_to', 'tester', 'due_date', 'dependencies'
        ]
        widgets = {
            'user_story': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'value': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'effort': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'tester': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'dependencies': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            from django.contrib.auth.models import User
            users = User.objects.filter(projectmember__project=project)
            self.fields['assigned_to'].queryset = users
            self.fields['tester'].queryset = users
            self.fields['user_story'].queryset = UserStory.objects.filter(project=project)
            self.fields['dependencies'].queryset = Ticket.objects.filter(user_story__project=project)
            if self.instance and self.instance.pk:
                self.fields['dependencies'].queryset = self.fields['dependencies'].queryset.exclude(pk=self.instance.pk)

class TicketStatusForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm', 'onchange': 'this.form.submit()'}),
        }

class TicketAcceptanceCriterionForm(forms.ModelForm):
    class Meta:
        model = TicketAcceptanceCriterion
        fields = ['description']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nuevo criterio de aceptación'}),
        }

TicketAcceptanceCriterionFormSet = inlineformset_factory(
    Ticket, TicketAcceptanceCriterion,
    form=TicketAcceptanceCriterionForm,
    extra=1,
    can_delete=True
)
