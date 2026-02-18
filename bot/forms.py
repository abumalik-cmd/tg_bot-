from django import forms
from .models import GlobalLesson


class ScheduleSelectionForm(forms.Form):
    grade = forms.IntegerField(
        label='Класс',
        min_value=1,
        max_value=11,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    letter = forms.ChoiceField(
        label='Буква',
        choices=[('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    day = forms.ChoiceField(
        label='День недели',
        choices=GlobalLesson.DAY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class LessonAddForm(forms.Form):
    number = forms.IntegerField(
        label='Номер урока',
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        label='Предмет',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название предмета'})
    )
    
    def __init__(self, *args, next_number=None, **kwargs):
        super().__init__(*args, **kwargs)
        if next_number and 'number' not in self.data:
            self.fields['number'].initial = next_number
