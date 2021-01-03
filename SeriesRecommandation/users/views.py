from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from api.neo4j_utils import Neo
from SeriesRecommandation.settings import NEO4J_PASSWORD, NEO4J_USER

neo = Neo("bolt://149.156.109.37:7687", (NEO4J_USER, NEO4J_PASSWORD))


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.data.get('password1')
            neo.create_user(username=username, password=password)
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

