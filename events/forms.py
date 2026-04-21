from django import forms
from .models import Category, Event, Participant

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'price', 'is_available', 'category']