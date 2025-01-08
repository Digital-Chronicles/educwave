from django.contrib.messages.context_processors import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser
from .forms import CustomAuthenticationForm

# Create your views here.
def user_login(request):
    if request == "POST":
        form = CustomAuthenticationForm(request=request, data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login Successfully. ")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password. ")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})