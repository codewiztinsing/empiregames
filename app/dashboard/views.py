from datetime import timedelta
from django.db.models import Sum
from django.core.paginator import Paginator
from django.utils import timezone
from users.models import User, SupportUser
from game.models import Game
from wallet.models import Transaction, WithdrawalRequest, Wallet
import requests
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from game.models import GameType
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .permissions import (
            admin_required, 
            support_required,
            admin_or_support_required,
            superuser_required,
            has_permission,
            check_user_role,
            user_can_access_resource
     )
from .tasks import send_message_to_all_players

def fetch_transaction_data_from_api():
    """Fetch transaction data from API"""
    try:
        # Get the base URL - you might need to adjust this based on your setup
        base_url = "http://localhost:8080"  # or your actual domain
        api_url = f"{base_url}/api/v1/wallet/transactions/stats/"
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API request failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching data from API: {e}")
        return None

@admin_or_support_required
def dashboard(request):
    # Get data for last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # User statistics (still from database for now)
    new_users = User.objects.filter(created_at__gte=thirty_days_ago).count()
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Game statistics (still from database for now)
    games_played = Game.objects.filter(created_at__gte=thirty_days_ago).count()
    total_games = Game.objects.count()
    games_ended = Game.objects.filter(ended=True, created_at__gte=thirty_days_ago)
    total_winnings = sum(game.entry_fee for game in games_ended)
    last_30_days_commission = float(total_winnings) * 0.2
    
    # Try to fetch transaction data from API, fallback to database if API fails
    api_data = fetch_transaction_data_from_api()
    
    if api_data:
        # Use API data
        total_deposits = api_data.get('total_deposits', 0)
        total_withdrawals = api_data.get('total_withdrawals', 0)
        total_withdrawals_amount = api_data.get('total_withdrawals_amount', 0)
        total_deposits_amount = api_data.get('total_deposits_amount', 0)
        total_wallet_balance = api_data.get('total_wallet_balance', 0)
        pending_withdrawals = api_data.get('pending_withdrawals', 0)
        pending_withdrawals_amount = api_data.get('pending_withdrawals_amount', 0)
        revenue_growth = api_data.get('revenue_growth', 0)
        api_date_range = api_data.get('date_range', {})
        thirty_days_ago_str = api_date_range.get('from', thirty_days_ago.strftime('%m/%d/%Y'))
        today_str = api_date_range.get('to', timezone.now().strftime('%m/%d/%Y'))
        data_source = "API"
    else:
        # Fallback to database queries
        total_deposits = Transaction.objects.filter(type="DEPOSIT", created_at__gte=thirty_days_ago).count()
        total_withdrawals = Transaction.objects.filter(type="WITHDRAW", created_at__gte=thirty_days_ago).count()
        total_withdrawals_amount = Transaction.objects.filter(type="WITHDRAW", created_at__gte=thirty_days_ago).aggregate(Sum('amount'))['amount__sum'] or 0
        total_deposits_amount = Transaction.objects.filter(type="DEPOSIT", created_at__gte=thirty_days_ago).aggregate(Sum('amount'))['amount__sum'] or 0
        total_wallet_balance = Wallet.objects.aggregate(Sum('balance'))['balance__sum'] or 0
        pending_withdrawals = WithdrawalRequest.objects.filter(status='pending').count()
        pending_withdrawals_amount = WithdrawalRequest.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate growth percentages (comparing with previous 30 days)
        previous_period_start = timezone.now() - timedelta(days=60)
        previous_deposits_amount = Transaction.objects.filter(type="DEPOSIT", created_at__gte=previous_period_start, created_at__lt=thirty_days_ago).aggregate(Sum('amount'))['amount__sum'] or 0
        revenue_growth = ((total_deposits_amount - previous_deposits_amount) / previous_deposits_amount * 100) if previous_deposits_amount > 0 else 0
        
        thirty_days_ago_str = thirty_days_ago.strftime('%m/%d/%Y')
        today_str = timezone.now().strftime('%m/%d/%Y')
        data_source = "Database"
    
    # Calculate user and games growth (still from database)
    previous_period_start = timezone.now() - timedelta(days=60)
    previous_new_users = User.objects.filter(created_at__gte=previous_period_start, created_at__lt=thirty_days_ago).count()
    previous_games_played = Game.objects.filter(created_at__gte=previous_period_start, created_at__lt=thirty_days_ago).count()
    
    user_growth = ((new_users - previous_new_users) / previous_new_users * 100) if previous_new_users > 0 else 0
    games_growth = ((games_played - previous_games_played) / previous_games_played * 100) if previous_games_played > 0 else 0

    context = {
        'page_title': 'Dashboard',
        'new_users': new_users,
        'total_users': total_users,
        'active_users': active_users,
        'games_played': games_played,
        'total_games': total_games,
        'total_winnings': total_winnings,
        'last_30_days_commission': last_30_days_commission,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_withdrawals_amount': total_withdrawals_amount,
        'total_deposits_amount': total_deposits_amount,
        'total_wallet_balance': total_wallet_balance,
        'pending_withdrawals': pending_withdrawals,
        'pending_withdrawals_amount': pending_withdrawals_amount,
        'user_growth': round(user_growth, 1),
        'games_growth': round(games_growth, 1),
        'revenue_growth': round(revenue_growth, 1),
        'thirty_days_ago': thirty_days_ago_str,
        'today': today_str,
        'data_source': data_source,  # For debugging
    }
    return render(request, 'dashboard/index.html', context)

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


def games(request):
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    limit = int(request.GET.get('limit', 20))
    page = int(request.GET.get('page', 1))
    user_id = request.GET.get('user_id', '')
    
    # Try to fetch data from API
    api_data = None
    try:
        base_url = "http://localhost:8080"
        
        if user_id:
            api_url = f"{base_url}/api/v1/game/games/by-user/"
            params = {'user_id': user_id, 'limit': limit * 2}
        elif status_filter:
            api_url = f"{base_url}/api/v1/game/games/by-status/"
            params = {'status': status_filter, 'limit': limit * 2}
        else:
            api_url = f"{base_url}/api/v1/game/games/recent/"
            params = {'limit': limit * 2}
            
        response = requests.get(api_url, params=params, timeout=10)
        if response.status_code == 200:
            api_data = response.json()
    except Exception as e:
        print(f"Error fetching games from API: {e}")
    
    # Get games statistics from API
    stats_data = None
    try:
        stats_url = f"{base_url}/api/v1/game/games/stats/"
        stats_response = requests.get(stats_url, timeout=10)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
    except Exception as e:
        print(f"Error fetching games stats from API: {e}")
    
    if api_data:
        # Use API data
        games_list = api_data.get('games', [])
        
        # Simple pagination for API data
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_games = games_list[start_idx:end_idx]
        
        # Create a simple paginator-like object
        class APIPaginator:
            def __init__(self, data, per_page):
                self.data = data
                self.per_page = per_page
                self.count = len(data)
                self.num_pages = (self.count + per_page - 1) // per_page
                
            def get_page(self, page_num):
                start_idx = (page_num - 1) * self.per_page
                end_idx = start_idx + self.per_page
                return self.data[start_idx:end_idx]
        
        paginator = APIPaginator(games_list, limit)
        page_obj = paginator.get_page(page)
        data_source = "API"
    else:
        # Fallback to database
        games = Game.objects.all().order_by('-id')
        if status_filter:
            games = games.filter(status=status_filter)
        
        paginator = Paginator(games, limit)
        page_obj = paginator.get_page(page)
        data_source = "Database"
    
    # Get summary statistics
    if stats_data:
        total_games = stats_data.get('total_games', 0)
        active_games = stats_data.get('active_games', 0)
        completed_today = stats_data.get('completed_today', 0)
        total_revenue = stats_data.get('total_revenue', 0)
    else:
        # Fallback to database calculation
        total_games = Game.objects.count()
        active_games = Game.objects.filter(ended=False).count()
        completed_today = Game.objects.filter(
            ended=True, 
            created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        total_revenue = Game.objects.filter(ended=True).aggregate(Sum('entry_fee'))['entry_fee__sum'] or 0
    
    context = {
        'games': page_obj,
        'page_title': 'Games',
        'page_obj': page_obj,
        'total_games': total_games,
        'active_games': active_games,
        'completed_today': completed_today,
        'total_revenue': total_revenue,
        'data_source': data_source,
        'current_status': status_filter,
        'current_user_id': user_id,
    }
    return render(request, 'dashboard/games.html', context)

def payments(request):
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    
    # Filter withdrawal requests based on status
    withdrawal_requests = WithdrawalRequest.objects.all().order_by('-created_at')
    
    if status_filter != 'all':
        withdrawal_requests = withdrawal_requests.filter(status=status_filter)
    
    paginator = Paginator(withdrawal_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'withdrawal_requests': page_obj,
        'page_title': 'Payments',
        'page_obj': page_obj,
        'current_status': status_filter,
        'status_choices': ['all', 'pending', 'success', 'failed']
    }
    return render(request, 'dashboard/payments.html', context)


def transcations(request):
    # Get filter parameters
    transaction_type = request.GET.get('type', '')
    limit = int(request.GET.get('limit', 20))
    page = int(request.GET.get('page', 1))
    
    # Try to fetch data from API
    api_data = None
    try:
        base_url = "http://localhost:8080"
        api_url = f"{base_url}/api/v1/wallet/transactions/recent/"
        
        params = {'limit': limit * 2}  # Fetch more to account for pagination
        if transaction_type:
            api_url = f"{base_url}/api/v1/wallet/transactions/by-type/"
            params['transaction_type'] = transaction_type
            
        response = requests.get(api_url, params=params, timeout=10)
        if response.status_code == 200:
            api_data = response.json()
    except Exception as e:
        print(f"Error fetching transactions from API: {e}")
    
    # Get transaction statistics from API
    stats_data = None
    try:
        stats_url = f"{base_url}/api/v1/wallet/transactions/stats/"
        stats_response = requests.get(stats_url, timeout=10)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
    except Exception as e:
        print(f"Error fetching transaction stats from API: {e}")
    
    if api_data:
        # Use API data
        transactions_list = api_data.get('transactions', [])
        total_count = api_data.get('count', 0)
        
        # Simple pagination for API data
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_transactions = transactions_list[start_idx:end_idx]
        
        # Create a simple paginator-like object
        class APIPaginator:
            def __init__(self, data, per_page):
                self.data = data
                self.per_page = per_page
                self.count = len(data)
                self.num_pages = (self.count + per_page - 1) // per_page
                
            def get_page(self, page_num):
                start_idx = (page_num - 1) * self.per_page
                end_idx = start_idx + self.per_page
                return self.data[start_idx:end_idx]
        
        paginator = APIPaginator(transactions_list, limit)
        page_obj = paginator.get_page(page)
        data_source = "API"
    else:
        # Fallback to database
        transactions = Transaction.objects.all()
        if transaction_type:
            transactions = transactions.filter(type=transaction_type)
        
        paginator = Paginator(transactions, limit)
        page_obj = paginator.get_page(page)
        data_source = "Database"
    
    # Get summary statistics
    if stats_data:
        total_deposits_amount = stats_data.get('total_deposits_amount', 0)
        total_withdrawals_amount = stats_data.get('total_withdrawals_amount', 0)
        net_amount = total_deposits_amount - total_withdrawals_amount
    else:
        # Fallback to database calculation
        total_deposits_amount = Transaction.objects.filter(type='DEPOSIT').aggregate(Sum('amount'))['amount__sum'] or 0
        total_withdrawals_amount = Transaction.objects.filter(type='WITHDRAW').aggregate(Sum('amount'))['amount__sum'] or 0
        net_amount = total_deposits_amount - total_withdrawals_amount
    
    context = {
        'transactions': page_obj,
        'page_title': 'Transactions',
        'page_obj': page_obj,
        'total_deposits_amount': total_deposits_amount,
        'total_withdrawals_amount': total_withdrawals_amount,
        'net_amount': net_amount,
        'data_source': data_source,
        'current_type': transaction_type,
    }
    return render(request, 'dashboard/transcations.html', context)

def users(request):
    users = User.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_users = users.count()
    suspended_users = users.filter(is_active=False).count()
    # handle next and previous page
    has_next = page_obj.has_next()
    has_previous = page_obj.has_previous()
    next_page = page_obj.next_page_number() if has_next else None
    previous_page = page_obj.previous_page_number() if has_previous else None
    
    context = {
        'users': page_obj,
        'page_title': 'Users',
        'page_obj': page_obj,
        'total_users': total_users,
        'suspended_users': suspended_users,
        'next_page': next_page,
        'previous_page': previous_page,
        'has_next': has_next,
        'has_previous': has_previous
    }
    return render(request, 'dashboard/users.html', context)


def bingo_cards(request):
    return render(request, 'dashboard/bingo_cards.html')

def referrals(request):
    # Get filter parameters
    bonus_status = request.GET.get('bonus_status', '')
    withdrawal_status = request.GET.get('withdrawal_status', '')
    limit = int(request.GET.get('limit', 20))
    
    # Try to fetch data from API
    api_data = None
    try:
        base_url = "http://localhost:8080"
        
        # Get referral statistics
        stats_url = f"{base_url}/api/v1/referrals/referrals/stats/"
        stats_response = requests.get(stats_url, timeout=10)
        if stats_response.status_code == 200:
            api_data = stats_response.json()
    except Exception as e:
        print(f"Error fetching referral data from API: {e}")
    
    # Get bonuses data
    bonuses_data = None
    try:
        bonuses_url = f"{base_url}/api/v1/referrals/referrals/bonuses/"
        params = {'limit': limit}
        if bonus_status:
            params['status'] = bonus_status
        bonuses_response = requests.get(bonuses_url, params=params, timeout=10)
        if bonuses_response.status_code == 200:
            bonuses_data = bonuses_response.json()
    except Exception as e:
        print(f"Error fetching referral bonuses from API: {e}")
    
    # Get withdrawals data
    withdrawals_data = None
    try:
        withdrawals_url = f"{base_url}/api/v1/referrals/referrals/withdrawals/"
        params = {'limit': limit}
        if withdrawal_status:
            params['status'] = withdrawal_status
        withdrawals_response = requests.get(withdrawals_url, params=params, timeout=10)
        if withdrawals_response.status_code == 200:
            withdrawals_data = withdrawals_response.json()
    except Exception as e:
        print(f"Error fetching referral withdrawals from API: {e}")
    
    context = {
        'api_data': api_data,
        'bonuses_data': bonuses_data,
        'withdrawals_data': withdrawals_data,
        'current_bonus_status': bonus_status,
        'current_withdrawal_status': withdrawal_status,
        'data_source': "API" if api_data else "Database",
        'page_title': 'Referral Management'
    }
    return render(request, 'dashboard/referrals.html', context)

def messages_view(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        send_message_to_all_players.delay(message)
        messages.success(request, 'Message sent successfully.')
        return redirect('dashboard:messages')
    return render(request, 'dashboard/messages.html')

def contact(request):
    users = SupportUser.objects.all()
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_users = users.count()
    has_next = page_obj.has_next()
    has_previous = page_obj.has_previous()
    next_page = page_obj.next_page_number() if has_next else None
    previous_page = page_obj.previous_page_number() if has_previous else None
    return render(request, 'dashboard/contact.html', {'users': page_obj, 'total_users': total_users, 'has_next': has_next, 'has_previous': has_previous, 'next_page': next_page, 'previous_page': previous_page})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@admin_or_support_required
def approve_withdrawal_request(request, request_id):
    """Approve a withdrawal request"""
    if request.method == 'POST':
        try:
            withdrawal_request = get_object_or_404(WithdrawalRequest, id=request_id)
            
            if withdrawal_request.status != 'pending':
                return JsonResponse({'success': False, 'message': 'This request has already been processed.'})
            
            # Update withdrawal request status
            withdrawal_request.status = 'success'
            withdrawal_request.save()
            
            # Create a transaction record
            Transaction.objects.create(
                user=withdrawal_request.user,
                amount=withdrawal_request.amount,
                type='WITHDRAW',
                status='success',
                reference=f'WR-{withdrawal_request.id}'
            )
            
            # Update user's wallet balance
            wallet = withdrawal_request.user.wallet
            wallet.balance -= withdrawal_request.amount
            wallet.save()
            
            return JsonResponse({'success': True, 'message': 'Withdrawal request approved successfully.'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@admin_or_support_required
def reject_withdrawal_request(request, request_id):
    """Reject a withdrawal request"""
    if request.method == 'POST':
        try:
            withdrawal_request = get_object_or_404(WithdrawalRequest, id=request_id)
            
            if withdrawal_request.status != 'pending':
                return JsonResponse({'success': False, 'message': 'This request has already been processed.'})
            
            # Update withdrawal request status
            withdrawal_request.status = 'failed'
            withdrawal_request.save()
            
            return JsonResponse({'success': True, 'message': 'Withdrawal request rejected successfully.'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



