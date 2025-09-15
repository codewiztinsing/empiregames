from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import User, SupportUser



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard:dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')



def user_details(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, 'dashboard/user_details.html', {'user': user})

def block_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('dashboard:users')

def unblock_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('dashboard:users')


def create_support_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.create_user(username=username, password=password)
        SupportUser.objects.create(user=user)
        return redirect('dashboard:users')
    return render(request, 'dashboard/create_support_user.html')


def delete_support_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('dashboard:users')

def update_support_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.role = request.POST['role']
    user.save()
    return redirect('dashboard:users')

def support_users(request):
    users = SupportUser.objects.all()
    return render(request, 'dashboard/support_users.html', {'users': users})