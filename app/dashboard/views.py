from datetime import timedelta
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from users.models import User
from game.models import Game
from wallet.models import Transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from game.models import GameType
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Agent
from django.db import transaction
import logging
from .permissions import (
            admin_required, 
            support_required,
            admin_or_support_required,
            superuser_required,
            has_permission,
            check_user_role,
            user_can_access_resource
     )

logger = logging.getLogger(__name__)

@login_required
@admin_or_support_required
def dashboard(request):
    new_users = User.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()
    games_played = Game.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()
    # get all games that have ended
    games_ended = Game.objects.filter(ended=True, created_at__gte=timezone.now() - timedelta(days=30))
    total_winnings = sum(game.entry_fee for game in games_ended)
    last_30_days_commission = float(total_winnings) * 0.2
    total_deposits = Transaction.objects.filter(type="DEPOSIT", created_at__gte=timezone.now() - timedelta(days=30)).count()
    total_withdrawals = Transaction.objects.filter(type="WITHDRAW", created_at__gte=timezone.now() - timedelta(days=30)).count()
    total_withdrawals_amount = Transaction.objects.filter(type="WITHDRAW", created_at__gte=timezone.now() - timedelta(days=30)).aggregate(Sum('amount'))['amount__sum'] or 0
    total_deposits_amount = Transaction.objects.filter(type="DEPOSIT", created_at__gte=timezone.now() - timedelta(days=30)).aggregate(Sum('amount'))['amount__sum'] or 0
   

    context = {
        'page_title': 'Dashboard',
        'new_users': new_users,
        'games_played': games_played,
        'last_30_days_commission': last_30_days_commission,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_withdrawals_amount': total_withdrawals_amount,
        'total_deposits_amount': total_deposits_amount
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def game_types(request):  
    if request.method == 'POST':
        # Check if it's a JSON request (from AJAX) or form request
        if request.content_type == 'application/json':
            # Handle JSON request from AJAX
            import json
            try:
                data = json.loads(request.body)
                bet_amount = data.get('bet_amount')
                commission = data.get('commission')
                
                if bet_amount and commission:
                    game_type = GameType.objects.create(
                        bet_amount=int(bet_amount),
                        commission=int(commission)
                    )
                    return JsonResponse({'success': True, 'message': 'Game type created successfully!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Please provide bet amount and commission.'}, status=400)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
        else:
            # Handle form request (original functionality)
            bet_amount = request.POST.get('bet_amount')
            commission = request.POST.get('commission')
            
            if bet_amount and commission:
                GameType.objects.create(
                    bet_amount=int(bet_amount),
                    commission=int(commission)
                )
                messages.success(request, 'Game type created successfully!')
            else:
                messages.error(request, 'Please provide both bet amount and commission.')
            
            return redirect('dashboard:game_types')
    
    elif request.method == 'PUT':
        # Update game type
        import json
        data = json.loads(request.body)
        game_type_id = data.get('id')
        bet_amount = data.get('bet_amount')
        commission = data.get('commission')
        
        try:
            game_type = get_object_or_404(GameType, id=game_type_id)
            if bet_amount:
                game_type.bet_amount = int(bet_amount)
            if commission:
                game_type.commission = int(commission)
            game_type.save()
            return JsonResponse({'success': True, 'message': 'Game type updated successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        # Delete game type
        import json
        data = json.loads(request.body)
        game_type_id = data.get('id')
        
        try:
            game_type = get_object_or_404(GameType, id=game_type_id)
            game_type.delete()
            return JsonResponse({'success': True, 'message': 'Game type deleted successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    # GET request - display all game types
    game_types = GameType.objects.all().order_by('-id')
    context = {
        'game_types': game_types,
        'page_title': 'Game Types'
    }
    return render(request, 'dashboard/game_types.html',context)


@login_required
def game_type_detail(request, game_type_id):
    """Handle individual game type operations (GET, PUT, DELETE)"""
    if request.method == 'PUT':
        # Update game type
        import json
        try:
            data = json.loads(request.body)
            game_type = get_object_or_404(GameType, id=game_type_id)
            
            # Update fields if provided
            if 'bet_amount' in data:
                game_type.bet_amount = int(data['bet_amount'])
            if 'commission' in data:
                game_type.commission = int(data['commission'])
            
            game_type.save()
            return JsonResponse({'success': True, 'message': 'Game type updated successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    elif request.method == 'DELETE':
        # Delete game type
        try:
            game_type = get_object_or_404(GameType, id=game_type_id)
            game_type.delete()
            return JsonResponse({'success': True, 'message': 'Game type deleted successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    else:
        # GET request - return game type details
        game_type = get_object_or_404(GameType, id=game_type_id)
        return JsonResponse({
            'id': game_type.id,
            'bet_amount': game_type.bet_amount,
            'commission': game_type.commission
        })


@login_required
def games(request):
    games = Game.objects.all().order_by('-id')
    paginator = Paginator(games, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'games': page_obj,
        'page_title': 'Games',
        'page_obj': page_obj
    }
    return render(request, 'dashboard/games.html',context)

@login_required
def payments(request):
    return render(request, 'dashboard/payments.html')


@login_required
def transcations(request):
    return render(request, 'dashboard/transcations.html')

@login_required
def users(request):
    # Filter users with agent codes
    users_with_agents = User.objects.filter(agent_code__isnull=False).exclude(agent_code='').order_by('-created_at')
    paginator = Paginator(users_with_agents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    total_users_with_agents = users_with_agents.count()
    total_users = User.objects.count()
    conversion_rate = (total_users_with_agents / total_users * 100) if total_users > 0 else 0
    
    context = {
        'users': page_obj,
        'total_users_with_agents': total_users_with_agents,
        'total_users': total_users,
        'conversion_rate': conversion_rate,
        'page_title': 'Users with Agent Codes',
        'page_obj': page_obj
    }
    return render(request, 'dashboard/users.html', context)

@login_required
@admin_required
def users_with_agents_api(request):
    """API endpoint to get users with agent codes"""
    try:
        # Filter users with agent codes
        users_with_agents = User.objects.filter(
            agent_code__isnull=False
        ).exclude(
            agent_code=''
        ).order_by('-created_at')
        
        # Get query parameters
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        agent_code = request.GET.get('agent_code')
        
        # Filter by specific agent code if provided
        if agent_code:
            users_with_agents = users_with_agents.filter(agent_code=agent_code)
        
        # Apply pagination
        users_data = users_with_agents[offset:offset + limit]
        
        # Format response data
        users_list = []
        for user in users_data:
            users_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
                'telegram_id': user.telegram_id,
                'agent_code': user.agent_code,
                'created_at': user.created_at.isoformat(),
                'is_active': user.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'data': users_list,
            'total': users_with_agents.count(),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def bingo_cards(request):
    return render(request, 'dashboard/bingo_cards.html')


@login_required
def dashboard_messages(request):
    return render(request, 'dashboard/messages.html')

@login_required
def contact(request):
    return render(request, 'dashboard/contact.html')

@login_required
def logout(request):
    from django.contrib.auth import logout as django_logout
    django_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    # Redirect to accounts login (adjust if your login route differs)
    return redirect('/accounts/login/')


# Agent Management Views
@login_required
@admin_required
def agents(request):
    """List all agents"""
    agents = Agent.objects.all().order_by('-created_at')
    
    # Update statistics for all agents
    for agent in agents:
        agent.update_statistics()
    
    paginator = Paginator(agents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'agents': page_obj,
        'page_title': 'Agents',
        'page_obj': page_obj
    }
    return render(request, 'dashboard/agents.html', context)


@login_required
@admin_required
def create_agent(request):
    """Create a new agent"""
    if request.method == 'POST':
        try:
            logger.info("[create_agent] POST received. Data keys=%s", list(request.POST.keys()))
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            agent_code = request.POST.get('agent_code')
            commission_rate = request.POST.get('commission_rate', 5.00)
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            logger.debug(
                "[create_agent] Raw values name=%s phone=%s agent_code=%s commission_rate=%s username=%s email=%s",
                name, phone, agent_code, commission_rate, username, email
            )
            
            if not name or not phone or not agent_code or not username or not password:
                logger.warning("[create_agent] Missing required fields. name=%s phone=%s agent_code=%s username=%s password_present=%s",
                               bool(name), bool(phone), bool(agent_code), bool(username), bool(password))
                messages.error(request, 'Name, Phone, Agent Code, Username, and Password are required.')
                return render(request, 'dashboard/create_agent.html', {
                    'page_title': 'Create Agent',
                    'prefill': {
                        'name': name,
                        'phone': phone,
                        'agent_code': agent_code,
                        'username': username,
                        'email': email,
                        'commission_rate': commission_rate,
                    }
                })
            
            # Check if phone already exists
            if Agent.objects.filter(phone=phone).exists():
                logger.warning("[create_agent] Duplicate phone detected. phone=%s", phone)
                messages.error(request, 'Phone number already exists.')
                return render(request, 'dashboard/create_agent.html', {
                    'page_title': 'Create Agent',
                    'prefill': {
                        'name': name,
                        'phone': phone,
                        'agent_code': agent_code,
                        'username': username,
                        'email': email,
                        'commission_rate': commission_rate,
                    }
                })
            
            # Check if agent code already exists
            if Agent.objects.filter(agent_code=agent_code).exists():
                logger.warning("[create_agent] Duplicate agent_code detected. agent_code=%s", agent_code)
                messages.error(request, 'Agent code already exists.')
                return render(request, 'dashboard/create_agent.html', {
                    'page_title': 'Create Agent',
                    'prefill': {
                        'name': name,
                        'phone': phone,
                        'agent_code': agent_code,
                        'username': username,
                        'email': email,
                        'commission_rate': commission_rate,
                    }
                })
            
            # Check if username already exists
            if Agent.objects.filter(username=username).exists():
                logger.warning("[create_agent] Duplicate username detected. username=%s", username)
                messages.error(request, 'Username already exists.')
                return render(request, 'dashboard/create_agent.html', {
                    'page_title': 'Create Agent',
                    'prefill': {
                        'name': name,
                        'phone': phone,
                        'agent_code': agent_code,
                        'username': username,
                        'email': email,
                        'commission_rate': commission_rate,
                    }
                })
            
            # Normalize and validate commission_rate
            try:
                commission_rate_value = float(commission_rate)
            except Exception:
                logger.exception("[create_agent] Invalid commission_rate value. commission_rate=%s", commission_rate)
                messages.error(request, 'Invalid commission rate.')
                return render(request, 'dashboard/create_agent.html', {
                    'page_title': 'Create Agent',
                    'prefill': {
                        'name': name,
                        'phone': phone,
                        'agent_code': agent_code,
                        'username': username,
                        'email': email,
                        'commission_rate': commission_rate,
                    }
                })

            # Create agent
            logger.info("[create_agent] Creating agent record for username=%s agent_code=%s", username, agent_code)
            agent = Agent.objects.create(
                name=name,
                phone=phone,
                agent_code=agent_code,
                commission_rate=commission_rate_value,
                username=username,
                email=email
            )
            
            # Set password
            agent.set_password(password)
            agent.save()
            logger.info("[create_agent] Agent created successfully. id=%s username=%s", agent.id, agent.username)
            
            messages.success(request, f'Agent {name} created successfully with code {agent_code}.')
            return redirect('dashboard:agents')
            
        except Exception as e:
            logger.exception("[create_agent] Unexpected error during agent creation: %s", str(e))
            messages.error(request, f'Error creating agent: {str(e)}')
            return render(request, 'dashboard/create_agent.html', {
                'page_title': 'Create Agent',
                'prefill': {}
            })
    
    # GET request - show form
    context = {
        'page_title': 'Create Agent'
    }
    return render(request, 'dashboard/create_agent.html', context)


@login_required
@admin_required
def agent_detail(request, agent_id):
    """View agent details and statistics"""
    agent = get_object_or_404(Agent, id=agent_id)
    
    # Update agent statistics to reflect current data
    agent.update_statistics()
    
    # Get users registered with this agent code
    users_with_agent_code = User.objects.filter(agent_code=agent.agent_code).order_by('-created_at')
    
    # Get agent statistics based on actual users
    total_referrals = users_with_agent_code.count()
    active_referrals = users_with_agent_code.filter(is_active=True).count()
    total_commission = agent.total_earnings
    
    context = {
        'agent': agent,
        'total_referrals': total_referrals,
        'active_referrals': active_referrals,
        'total_commission': total_commission,
        'users_with_agent_code': users_with_agent_code,
        'page_title': f'Agent: {agent.name}'
    }
    return render(request, 'dashboard/agent_detail.html', context)



@login_required
@admin_required
def edit_agent(request, agent_id):
    """Update an existing agent"""
    agent = get_object_or_404(Agent, id=agent_id)
    if request.method == 'POST':
        try:
            name = request.POST.get('name', agent.name)
            phone = request.POST.get('phone', agent.phone)
            agent_code = request.POST.get('agent_code', agent.agent_code)
            commission_rate = request.POST.get('commission_rate', agent.commission_rate)
            username = request.POST.get('username', agent.username)
            email = request.POST.get('email', agent.email)
            is_active = request.POST.get('is_active') == 'on'

            # basic duplicates check excluding current agent
            if Agent.objects.filter(phone=phone).exclude(id=agent.id).exists():
                messages.error(request, 'Phone number already exists for another agent.')
                return redirect('dashboard:agent_detail', agent_id=agent.id)
            if Agent.objects.filter(agent_code=agent_code).exclude(id=agent.id).exists():
                messages.error(request, 'Agent code already exists for another agent.')
                return redirect('dashboard:agent_detail', agent_id=agent.id)
            if Agent.objects.filter(username=username).exclude(id=agent.id).exists():
                messages.error(request, 'Username already exists for another agent.')
                return redirect('dashboard:agent_detail', agent_id=agent.id)

            try:
                commission_rate_value = float(commission_rate)
            except Exception:
                messages.error(request, 'Invalid commission rate.')
                return redirect('dashboard:agent_detail', agent_id=agent.id)

            agent.name = name
            agent.phone = phone
            agent.agent_code = agent_code
            agent.commission_rate = commission_rate_value
            agent.username = username
            agent.email = email
            agent.is_active = is_active
            agent.save()

            messages.success(request, 'Agent updated successfully.')
            return redirect('dashboard:agent_detail', agent_id=agent.id)
        except Exception as e:
            logger.exception('[edit_agent] error: %s', str(e))
            messages.error(request, f'Error updating agent: {str(e)}')
            return redirect('dashboard:agent_detail', agent_id=agent.id)

    # GET - show a minimal edit page or redirect to detail (keeping UI simple)
    return redirect('dashboard:agent_detail', agent_id=agent.id)


@login_required
@admin_required
def delete_agent(request, agent_id):
    """Delete an agent (POST only)"""
    agent = get_object_or_404(Agent, id=agent_id)
    if request.method == 'POST':
        try:
            name = agent.name
            agent.delete()
            messages.success(request, f'Agent {name} deleted successfully.')
        except Exception as e:
            logger.exception('[delete_agent] error: %s', str(e))
            messages.error(request, f'Error deleting agent: {str(e)}')
        return redirect('dashboard:agents')
    messages.error(request, 'Invalid request method.')
    return redirect('dashboard:agent_detail', agent_id=agent.id)




