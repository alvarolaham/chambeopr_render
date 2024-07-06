from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'myapp/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'myapp/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(request, 'myapp/delete_account.html')

def home_services(request):
    services = [
        "Landscaping", "Gardening", "Painting", "House & Airbnb Cleaning",
        "Pest Control", "Roofing", "Interior Design", "Security Systems",
        "Solar Panel Installation", "Swimming Pool Maintenance", "Babysitting/Nanny Services",
        "Air Conditioning", "Construction & Remodeling", "Electrician", "Plumbing"
    ]
    return render(request, "myapp/home_services.html", {"services": services})
