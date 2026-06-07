from django import forms
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class CustomerLoginForm(forms.Form):
    username = forms.CharField(
        label='Email or Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email or username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'id': 'id_password'
        })
    )
    remember_me = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        username_input = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username_input and password:
            user_obj = None

            # check by email
            try:
                user_obj = User.objects.get(email=username_input)
                username_for_auth = user_obj.username
            except User.DoesNotExist:
                username_for_auth = username_input

            user = authenticate(username=username_for_auth, password=password)

            if not user:
                raise forms.ValidationError("Invalid username/email or password.")
            if not user.is_active:
                raise forms.ValidationError("This account is inactive.")

            cleaned_data['user'] = user

        return cleaned_data