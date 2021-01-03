from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# from .models import Profile


class UserRegisterForm(UserCreationForm):
    # default: required = True

    class Meta:
        model = User
        # now we know that when we'll do form.save() we'll save it to model User
        fields = ['username', 'password1', 'password2']