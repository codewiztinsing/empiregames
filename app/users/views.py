from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import User, SupportUser
import requests
import json



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
    # Try to fetch data from API
    api_data = None
    try:
        base_url = "http://localhost:8080"
        api_url = f"{base_url}/api/v1/users/{user_id}/details/"
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            api_data = response.json()
    except Exception as e:
        print(f"Error fetching user details from API: {e}")
    
    if api_data:
        # Use API data
        user_data = api_data.get('user', {})
        wallet_data = api_data.get('wallet', {})
        transactions_data = api_data.get('transactions', {})
        games_data = api_data.get('games', {})
        referrals_data = api_data.get('referrals', {})
        withdrawal_requests = api_data.get('withdrawal_requests', [])
        data_source = "API"
    else:
        # Fallback to database
        user = User.objects.get(id=user_id)
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'telegram_id': user.telegram_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'created_at': user.created_at,
            'referral_code': user.referral_code,
            'is_agent': user.is_agent,
            'sponsor_changed': user.sponsor_changed
        }
        wallet_data = {}
        transactions_data = {}
        games_data = {}
        referrals_data = {}
        withdrawal_requests = []
        data_source = "Database"
    
    context = {
        'user_data': user_data,
        'wallet_data': wallet_data,
        'transactions_data': transactions_data,
        'games_data': games_data,
        'referrals_data': referrals_data,
        'withdrawal_requests': withdrawal_requests,
        'data_source': data_source,
        'page_title': 'User Details'
    }
    return render(request, 'dashboard/user_details.html', context)

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