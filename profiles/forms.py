from django import forms
from django.contrib.auth.models import User
from .models import Profile
from .widgets import CustomClearableFileInput


class ProfileForm(forms.ModelForm):
    YEAR_CHOICES = [
        ('First Year', 'First Year'),
        ('Second Year', 'Second Year'),
        ('Third Year', 'Third Year'),
        ('Fourth Year', 'Fourth Year')
    ]

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
    )
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        exclude_admin_fields = kwargs.pop('exclude_admin_fields', False)
        super().__init__(*args, **kwargs)

        if exclude_admin_fields:
            del self.fields['year']
            del self.fields['major']
            del self.fields['bio']

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'year', 'major', 'computing_id', 'bio', 'profile_pic']
        widgets = {
            'major': forms.TextInput(attrs={'class': 'form-control'}),
            'computing_id': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'profile_pic': CustomClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/png, image/jpeg',  # Restrict file types
            }),
        }
