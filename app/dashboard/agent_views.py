from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Agent
from users.models import User
from wallet.models import Transaction
from .permissions import agent_required
import logging

logger = logging.getLogger(__name__)


def agent_login(request):
    """Agent login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'agent/login.html')
        
        try:
            agent = Agent.objects.get(username=username, is_active=True)
            if agent.check_password(password):
                # Set agent session
                request.session['agent_id'] = agent.id
                request.session['agent_name'] = agent.name
                messages.success(request, f'Welcome back, {agent.name}!')
                return redirect('agent:dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        except Agent.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'agent/login.html')


def agent_logout(request):
    """Agent logout view"""
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('agent:login')


@agent_required
def agent_dashboard(request):
    """Agent dashboard view"""
    agent = request.agent
    
    # Update agent statistics
    agent.update_statistics()
    # Ensure we have a referral link for this agent
    try:
        referral_link = agent.telegram_bot_link or agent.generate_telegram_bot_link()
        if not agent.telegram_bot_link:
            agent.telegram_bot_link = referral_link
            agent.save(update_fields=['telegram_bot_link'])
    except Exception:
        referral_link = None
    
    # Get agent's users
    agent_users = User.objects.filter(agent_code=agent.agent_code).order_by('-created_at')
    total_users = agent_users.count()
    active_users = agent_users.filter(is_active=True).count()
    
    # Get recent users (last 10)
    recent_users = agent_users[:10]
    
    # Get total deposits from agent's users
    total_deposits = Transaction.objects.filter(
        user__agent_code=agent.agent_code,
        type='DEPOSIT',
        status='success'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user__agent_code=agent.agent_code
    ).order_by('-created_at')[:10]
    
    context = {
        'agent': agent,
        'total_users': total_users,
        'active_users': active_users,
        'total_deposits': total_deposits,
        'total_earnings': agent.total_earnings,
        'recent_users': recent_users,
        'recent_transactions': recent_transactions,
        'referral_link': referral_link,
        'page_title': f'Agent Dashboard - {agent.name}'
    }
    
    return render(request, 'agent/dashboard.html', context)


@agent_required
def agent_users(request):
    """Agent's users management view"""
    agent = request.agent
    
    # Get agent's users
    agent_users = User.objects.filter(agent_code=agent.agent_code).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(agent_users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'agent': agent,
        'users': page_obj,
        'total_users': agent_users.count(),
        'page_title': f'My Users - {agent.name}'
    }
    
    return render(request, 'agent/users.html', context)


@agent_required
def agent_user_detail(request, user_id):
    """Agent's user detail view"""
    agent = request.agent
    
    try:
        user = User.objects.get(id=user_id, agent_code=agent.agent_code)
    except User.DoesNotExist:
        messages.error(request, 'User not found or not under your management.')
        return redirect('agent:users')
    
    # Get user's transactions
    user_transactions = Transaction.objects.filter(user=user).order_by('-created_at')
    
    # Get user's wallet balance
    from wallet.models import Wallet
    try:
        wallet = Wallet.objects.get(user=user)
        balance = wallet.balance
    except Wallet.DoesNotExist:
        balance = 0
    
    context = {
        'agent': agent,
        'user': user,
        'balance': balance,
        'transactions': user_transactions,
        'page_title': f'User Details - {user.username}'
    }
    
    return render(request, 'agent/user_detail.html', context)


@agent_required
def agent_commissions(request):
    """Agent's commissions view"""
    agent = request.agent
    
    # Get agent's earnings from transactions
    commission_transactions = Transaction.objects.filter(
        user__agent_code=agent.agent_code,
        type='COMMISSION'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(commission_transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate total commissions
    total_commissions = commission_transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'agent': agent,
        'commissions': page_obj,
        'total_commissions': total_commissions,
        'page_title': f'My Commissions - {agent.name}'
    }
    
    return render(request, 'agent/commissions.html', context)


@agent_required
def agent_profile(request):
    """Agent profile view"""
    agent = request.agent
    
    if request.method == 'POST':
        # Update agent profile
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        if name:
            agent.name = name
        if email:
            agent.email = email
        if phone:
            agent.phone = phone
        
        agent.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('agent:profile')
    
    context = {
        'agent': agent,
        'page_title': f'My Profile - {agent.name}'
    }
    
    return render(request, 'agent/profile.html', context)


@agent_required
def agent_change_password(request):
    """Agent change password view"""
    agent = request.agent
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not agent.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'agent/change_password.html', {'agent': agent})
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'agent/change_password.html', {'agent': agent})
        
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'agent/change_password.html', {'agent': agent})
        
        agent.set_password(new_password)
        agent.save()
        messages.success(request, 'Password changed successfully!')
        return redirect('agent:profile')
    
    context = {
        'agent': agent,
        'page_title': f'Change Password - {agent.name}'
    }
    
    return render(request, 'agent/change_password.html', context)
