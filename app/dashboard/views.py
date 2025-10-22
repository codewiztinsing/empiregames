from datetime import timedelta
from django.db.models import Sum
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from users.models import User, SupportUser
from game.models import Game
from wallet.models import Transaction, WithdrawalRequest, Wallet, PaymentSettings, ManualSession
# Referral services removed
from .permissions import admin_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from game.models import Game
import requests
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from game.models import GameRoom
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .permissions import (
            admin_required, 
            support_required,
            admin_or_support_required,
            superuser_required,
            has_permission,
            check_user_role,
            user_can_access_resource,
            roles_required,
     )
from .tasks import send_message_to_all_players
from decouple import config
import requests

from django.contrib.auth.models import Group, Permission
from django.apps import apps as django_apps

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
    games_ended = Game.objects.filter(ended_at__isnull=False, created_at__gte=thirty_days_ago)
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

@admin_required
def game_rooms(request):  
    if request.method == 'POST':
        # Additional authorization check for creating game rooms
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Insufficient permissions to create game rooms.'}, status=403)
        
        # Check if it's a JSON request (from AJAX) or form request
        if request.content_type == 'application/json':
            # Handle JSON request from AJAX
            import json
            try:
                data = json.loads(request.body)
                bet_amount = data.get('bet_amount')
                commission = data.get('commission')
                
                if bet_amount and commission:
                    # Validate input values
                    try:
                        bet_amount_decimal = Decimal(bet_amount)
                        commission_decimal = Decimal(commission)
                        
                        if bet_amount_decimal <= 0:
                            return JsonResponse({'success': False, 'message': 'Bet amount must be greater than 0.'}, status=400)
                        
                        if commission_decimal < 0 or commission_decimal > 100:
                            return JsonResponse({'success': False, 'message': 'Commission must be between 0 and 100.'}, status=400)
                        
                        game_type = GameRoom.objects.create(
                            name=f"Game Room {bet_amount} ETB",
                            entry_fee=bet_amount_decimal,
                            house_edge_percentage=commission_decimal,
                            created_by=request.user
                        )
                        return JsonResponse({'success': True, 'message': 'Game room created successfully!'})
                    except (ValueError, TypeError) as e:
                        return JsonResponse({'success': False, 'message': 'Invalid numeric values provided.'}, status=400)
                else:
                    return JsonResponse({'success': False, 'message': 'Please provide bet amount and commission.'}, status=400)
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
        else:
            # Handle form request (original functionality)
            bet_amount = request.POST.get('bet_amount')
            commission = request.POST.get('commission')
            
            if bet_amount and commission:
                try:
                    bet_amount_decimal = Decimal(bet_amount)
                    commission_decimal = Decimal(commission)
                    
                    if bet_amount_decimal <= 0:
                        messages.error(request, 'Bet amount must be greater than 0.')
                    elif commission_decimal < 0 or commission_decimal > 100:
                        messages.error(request, 'Commission must be between 0 and 100.')
                    else:
                        GameRoom.objects.create(
                            name=f"Game Room {bet_amount} ETB",
                            entry_fee=bet_amount_decimal,
                            house_edge_percentage=commission_decimal,
                            created_by=request.user
                        )
                        messages.success(request, 'Game room created successfully!')
                except (ValueError, TypeError):
                    messages.error(request, 'Invalid numeric values provided.')
            else:
                messages.error(request, 'Please provide both bet amount and commission.')
            
            return redirect('dashboard:game_rooms')
    
    elif request.method == 'PUT':
        # Additional authorization check for updating game rooms
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Insufficient permissions to update game rooms.'}, status=403)
        
        # Update game room
        import json
        data = json.loads(request.body)
        game_type_id = data.get('id')
        bet_amount = data.get('bet_amount')
        commission = data.get('commission')
        
        try:
            game_room = get_object_or_404(GameRoom, id=game_room_id)
            
            # Validate input values if provided
            if bet_amount:
                try:
                    bet_amount_decimal = Decimal(bet_amount)
                    if bet_amount_decimal <= 0:
                        return JsonResponse({'success': False, 'message': 'Bet amount must be greater than 0.'}, status=400)
                    game_room.entry_fee = bet_amount_decimal
                except (ValueError, TypeError):
                    return JsonResponse({'success': False, 'message': 'Invalid bet amount value.'}, status=400)
            
            if commission:
                try:
                    commission_decimal = Decimal(commission)
                    if commission_decimal < 0 or commission_decimal > 100:
                        return JsonResponse({'success': False, 'message': 'Commission must be between 0 and 100.'}, status=400)
                    game_room.house_edge_percentage = commission_decimal
                except (ValueError, TypeError):
                    return JsonResponse({'success': False, 'message': 'Invalid commission value.'}, status=400)
            
            game_room.save()
            return JsonResponse({'success': True, 'message': 'Game room updated successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        # Additional authorization check for deleting game rooms
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Insufficient permissions to delete game rooms.'}, status=403)
        
        # Delete game room
        import json
        data = json.loads(request.body)
        game_type_id = data.get('id')
        
        try:
            game_room = get_object_or_404(GameRoom, id=game_room_id)
            
            # Check if game room is being used in active games
            active_games = Game.objects.filter(room=game_room, ended_at__isnull=True)
            if active_games.exists():
                return JsonResponse({'success': False, 'message': 'Cannot delete game room with active games.'}, status=400)
            
            game_room.delete()
            return JsonResponse({'success': True, 'message': 'Game room deleted successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    # GET request - display all game rooms
    game_rooms = GameRoom.objects.all().order_by('-id')
    context = {
        'game_rooms': game_rooms,
        'page_title': 'Game Rooms'
    }
    return render(request, 'dashboard/game_rooms.html', context)


@admin_required
def game_room_detail(request, game_room_id):
    """Handle individual game room operations (GET, PUT, DELETE)"""
    if request.method == 'PUT':
        # Additional authorization check for updating game rooms
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Insufficient permissions to update game rooms.'}, status=403)
        
        # Update game room
        import json
        try:
            data = json.loads(request.body)
            game_room = get_object_or_404(GameRoom, id=game_room_id)
            
            # Update fields if provided with validation
            if 'bet_amount' in data:
                try:
                    bet_amount_decimal = Decimal(data['bet_amount'])
                    if bet_amount_decimal <= 0:
                        return JsonResponse({'success': False, 'message': 'Bet amount must be greater than 0.'}, status=400)
                    game_room.entry_fee = bet_amount_decimal
                except (ValueError, TypeError):
                    return JsonResponse({'success': False, 'message': 'Invalid bet amount value.'}, status=400)
            
            if 'commission' in data:
                try:
                    commission_decimal = Decimal(data['commission'])
                    if commission_decimal < 0 or commission_decimal > 100:
                        return JsonResponse({'success': False, 'message': 'Commission must be between 0 and 100.'}, status=400)
                    game_room.house_edge_percentage = commission_decimal
                except (ValueError, TypeError):
                    return JsonResponse({'success': False, 'message': 'Invalid commission value.'}, status=400)
            
            game_room.save()
            return JsonResponse({'success': True, 'message': 'Game room updated successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    elif request.method == 'DELETE':
        # Additional authorization check for deleting game rooms
        if not request.user.is_staff:
            return JsonResponse({'success': False, 'message': 'Insufficient permissions to delete game rooms.'}, status=403)
        
        # Delete game room
        try:
            game_room = get_object_or_404(GameRoom, id=game_room_id)
            
            # Check if game room is being used in active games
            active_games = Game.objects.filter(room=game_room, ended_at__isnull=True)
            if active_games.exists():
                return JsonResponse({'success': False, 'message': 'Cannot delete game room with active games.'}, status=400)
            
            game_room.delete()
            return JsonResponse({'success': True, 'message': 'Game room deleted successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    else:
        # GET request - return game room details
        game_room = get_object_or_404(GameRoom, id=game_room_id)
        return JsonResponse({
            'id': game_room.id,
            'bet_amount': str(game_room.entry_fee),
            'commission': str(game_room.house_edge_percentage)
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
        active_games = Game.objects.filter(ended_at__isnull=True).count()
        completed_today = Game.objects.filter(
            ended_at__isnull=False, 
            created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        total_revenue = Game.objects.filter(ended_at__isnull=False).aggregate(Sum('entry_fee'))['entry_fee__sum'] or 0
    
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

@roles_required('Admin', 'Support', 'Finance', 'superuser')
def payments(request):
    # Save settings when posted
    if request.method == 'POST':
        settings_obj = PaymentSettings.get_solo()
        try:
            settings_obj.min_deposit_amount = float(request.POST.get('min_deposit_amount') or 0)
            settings_obj.min_withdrawal_amount = float(request.POST.get('min_withdrawal_amount') or 0)
            settings_obj.max_withdrawal_amount = float(request.POST.get('max_withdrawal_amount') or 0)
            settings_obj.withdrawal_fee_percent = float(request.POST.get('withdrawal_fee_percent') or 0)
            settings_obj.save()
            messages.success(request, 'Payment settings saved successfully.')
        except Exception as e:
            messages.error(request, f'Failed to save settings: {e}')

    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    
    # Filter withdrawal requests based on status
    withdrawal_requests = WithdrawalRequest.objects.all().order_by('-created_at')
    
    if status_filter != 'all':
        withdrawal_requests = withdrawal_requests.filter(status=status_filter)
    
    paginator = Paginator(withdrawal_requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    settings_obj = PaymentSettings.get_solo()
    # Manual deposits list (successful manual sessions)
    manual_deposits = ManualSession.objects.filter(status="success").order_by('-created_at')[:100]
    
    context = {
        'withdrawal_requests': page_obj,
        'page_title': 'Payments',
        'page_obj': page_obj,
        'current_status': status_filter,
        'status_choices': ['all', 'pending', 'success', 'failed'],
        'settings': settings_obj,
        'manual_deposits': manual_deposits,
    }
    return render(request, 'dashboard/payments.html', context)


@superuser_required
def roles(request):
    groups = Group.objects.all().order_by('name')
    users = User.objects.all().order_by('username')

    # Build CRUD permissions matrix for project models
    project_app_labels = {
        'users', 'wallet', 'game', 'dashboard', 'referrals', 'webhooks'
    }
    permissions_matrix = []
    for model in django_apps.get_models():
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        if app_label not in project_app_labels:
            continue
        # Fetch standard CRUD perms for this model
        codenames = [f'add_{model_name}', f'change_{model_name}', f'delete_{model_name}', f'view_{model_name}']
        perms = list(Permission.objects.filter(content_type__app_label=app_label, content_type__model=model_name, codename__in=codenames).order_by('codename'))
        if not perms:
            continue
        permissions_matrix.append({
            'app_label': app_label,
            'model_name': model.__name__,
            'model_key': f"{app_label}.{model_name}",
            'permissions': perms,
        })

    context = {
        'groups': groups,
        'users': users,
        'permissions_matrix': permissions_matrix,
    }
    return render(request, 'dashboard/roles.html', context)


@superuser_required
def create_role(request):
    if request.method != 'POST':
        return redirect('dashboard:roles')
    name = (request.POST.get('name') or '').strip()
    if not name:
        messages.error(request, 'Role name required')
        return redirect('dashboard:roles')
    group, created = Group.objects.get_or_create(name=name)

    # Assign selected permissions if provided
    perm_ids = request.POST.getlist('permissions')
    if perm_ids:
        selected_perms = Permission.objects.filter(id__in=perm_ids)
        group.permissions.set(selected_perms)
    if created:
        messages.success(request, f"Role '{group.name}' created")
    else:
        messages.info(request, f"Role '{group.name}' updated")
    return redirect('dashboard:roles')


@superuser_required
def assign_role(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)
    group_name = (request.POST.get('group') or '').strip()
    user = get_object_or_404(User, id=user_id)
    group = Group.objects.filter(name=group_name).first()
    if not group:
        return JsonResponse({'success': False, 'message': 'Role not found'}, status=404)
    user.groups.add(group)
    return JsonResponse({'success': True})


@superuser_required
def remove_role(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)
    group_name = (request.POST.get('group') or '').strip()
    user = get_object_or_404(User, id=user_id)
    group = Group.objects.filter(name=group_name).first()
    if not group:
        return JsonResponse({'success': False, 'message': 'Role not found'}, status=404)
    user.groups.remove(group)
    return JsonResponse({'success': True})

@admin_or_support_required
def add_manual_deposit(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    try:
        phone = request.POST.get('phone')
        amount = float(request.POST.get('amount') or 0)
        reference = request.POST.get('reference') or ''
        if not phone or amount <= 0:
            return JsonResponse({'success': False, 'message': 'Phone and positive amount required'}, status=400)

        user = User.objects.filter(phone=phone).first()
        if not user:
            return JsonResponse({'success': False, 'message': 'User not found'}, status=404)

        wallet = Wallet.objects.filter(user=user).first()
        if not wallet:
            wallet = Wallet.objects.create(user=user, balance=0)

        wallet.balance += amount
        wallet.save()

        Transaction.objects.create(
            user=user,
            amount=amount,
            type='DEPOSIT',
            status='success',
            reference=reference or 'manual-dashboard'
        )

        # Create a ManualSession record for visibility
        ManualSession.objects.create(
            session_id=reference or 'manual-dashboard',
            phone_number=phone,
            amount=amount,
            transaction_number=None,
            status='success'
        )

        # Notify user via Telegram if possible
        if getattr(user, 'telegram_id', None):
            try:
                bot_token = config('BOT_TOKEN')
                telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                message = (
                    f"🎉 Deposit Successful! 🎉\n\n"
                    f"💰 Amount: {amount} ETB\n"
                    f"💎 Total Credited: {amount} ETB\n"
                    f"📊 New Balance: {wallet.balance} ETB\n"
                    f"🔗 Reference: {reference or 'manual-dashboard'}\n\n"
                    f"✅ Your account has been credited successfully!"
                )
                requests.post(telegram_url, json={'chat_id': user.telegram_id, 'text': message, 'parse_mode': 'HTML'})
            except Exception:
                pass

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


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
    
    # Calculate wallet balance for each user
    users_with_bonuses = []
    for user in page_obj:
        # Get wallet balance
        wallet_balance = 0.0
        try:
            wallet = Wallet.objects.get(user=user)
            wallet_balance = wallet.balance
        except Wallet.DoesNotExist:
            pass
        
        # Calculate total balance (wallet + referral earnings)
        total_balance = wallet_balance + float(user.total_referral_earnings or 0)
        
        users_with_bonuses.append({
            'user': user,
            'wallet_balance': wallet_balance,
            'total_balance': total_balance,
        })
    
    # handle next and previous page
    has_next = page_obj.has_next()
    has_previous = page_obj.has_previous()
    next_page = page_obj.next_page_number() if has_next else None
    previous_page = page_obj.previous_page_number() if has_previous else None
    
    context = {
        'users': page_obj,
        'users_with_bonuses': users_with_bonuses,
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


@admin_required
def user_create(request):
    context = { 'page_title': 'Create User' }
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        telegram_id = (request.POST.get('telegram_id') or '').strip()
        password = (request.POST.get('password') or '').strip()
        if not username or not phone or not telegram_id or not password:
            messages.error(request, 'All fields are required')
            return render(request, 'dashboard/user_create.html', context)
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'dashboard/user_create.html', context)
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone already exists')
            return render(request, 'dashboard/user_create.html', context)
        if User.objects.filter(telegram_id=telegram_id).exists():
            messages.error(request, 'Telegram ID already exists')
            return render(request, 'dashboard/user_create.html', context)
        try:
            # Use Django's create_user method which properly handles password hashing
            user = User.objects.create_user(
                username=username,
                phone=phone,
                telegram_id=telegram_id,
                password=password,
            )
            Wallet.objects.get_or_create(user=user)
            messages.success(request, 'User created successfully')
            return redirect('dashboard:users')
        except Exception as e:
            messages.error(request, f'Failed to create user: {e}')
            return render(request, 'dashboard/user_create.html', context)
    return render(request, 'dashboard/user_create.html', context)

@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)
    wallet = Wallet.objects.filter(user=user).first()
    context = {'user_obj': user, 'wallet': wallet, 'page_title': 'Edit User'}
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone', '').strip()
        is_agent = request.POST.get('is_agent') == 'on'
        referred_by_telegram = request.POST.get('referred_by_telegram', '').strip()
        balance = request.POST.get('balance', '').strip()

        if username:
            user.username = username
        if phone:
            user.phone = phone
        user.is_agent = is_agent

        # Update referred_by using referrer's telegram_id if provided
        if referred_by_telegram:
            try:
                referrer = User.objects.get(telegram_id=str(referred_by_telegram))
                
                # Prevent self-referral
                if referrer.id == user.id:
                    context['error'] = 'Cannot set user as their own referrer.'
                    return render(request, 'dashboard/user_edit.html', context)
                
                user.referred_by = referrer
            except User.DoesNotExist:
                context['error'] = 'Referrer with that Telegram ID not found.'
                return render(request, 'dashboard/user_edit.html', context)
        else:
            user.referred_by = None

        user.save()
        
        # Update wallet balance if provided
        if balance != '':
            if not wallet:
                wallet = Wallet.objects.create(user=user, balance=0)
            wallet.balance = float(balance)
            wallet.save()
        return redirect('dashboard:users')

    return render(request, 'dashboard/user_edit.html', context)


@admin_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('dashboard:users')
    return render(request, 'dashboard/user_delete_confirm.html', {'user_obj': user, 'page_title': 'Delete User'})


@admin_required
def user_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    wallet = Wallet.objects.filter(user=user).first()
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:50]
    # Referral bonuses removed
    referral_withdrawals = WithdrawalRequest.objects.filter(user=user).order_by('-created_at')[:50]
    # PlayerGame removed; show recent games instead
    player_games = []
    recent_games = Game.objects.order_by('-created_at')[:50]

    # Get all users referred by this user with their generation levels
    referred_users = []
    
    # First generation (direct referrals)
    first_gen_users = User.objects.filter(referred_by=user).select_related('referred_by')
    for ref_user in first_gen_users:
        referred_users.append({
            'user': ref_user,
            'generation': '1st Generation',
            'level': 1
        })
    
    # Second generation (referrals of referrals)
    second_gen_users = User.objects.filter(referred_by__referred_by=user).select_related('referred_by', 'referred_by__referred_by')
    for ref_user in second_gen_users:
        referred_users.append({
            'user': ref_user,
            'generation': '2nd Generation', 
            'level': 2
        })
    
    # Sort by generation level and creation date
    referred_users.sort(key=lambda x: (x['level'], x['user'].created_at), reverse=True)
    
    # Calculate generation counts
    first_gen_count = len([u for u in referred_users if u['level'] == 1])
    second_gen_count = len([u for u in referred_users if u['level'] == 2])

    # Legacy/referrals app data if present
    legacy_bonuses = []
    user_stats = None

    context = {
        'page_title': f'User Details - {user.username}',
        'user_obj': user,
        'wallet': wallet,
        'transactions': transactions,
        'referral_bonuses': referral_bonuses,
        'referral_withdrawals': referral_withdrawals,
        'player_games': player_games,
        'referred_users': referred_users,
        'first_gen_count': first_gen_count,
        'second_gen_count': second_gen_count,
        'legacy_bonuses': legacy_bonuses,
        'user_stats': user_stats,
    }
    return render(request, 'dashboard/user_details.html', context)
def bingo_cards(request):
    from django.http import HttpResponseNotFound
    return HttpResponseNotFound()

# Referrals view removed

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
            # Notify user via Telegram
            try:
                if getattr(withdrawal_request.user, 'telegram_id', None):
                    bot_token = config('BOT_TOKEN')
                    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    text = (
                        f"✅ Withdrawal Approved\n\n"
                        f"💸 Amount: {withdrawal_request.amount} ETB\n"
                        f"📌 Status: Success\n"
                        f"🔗 Reference: WR-{withdrawal_request.id}"
                    )
                    requests.post(telegram_url, json={'chat_id': withdrawal_request.user.telegram_id, 'text': text, 'parse_mode': 'HTML'})
            except Exception:
                pass
            
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
            # Notify user via Telegram
            try:
                if getattr(withdrawal_request.user, 'telegram_id', None):
                    bot_token = config('BOT_TOKEN')
                    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    text = (
                        f"❌ Withdrawal Rejected\n\n"
                        f"💸 Amount: {withdrawal_request.amount} ETB\n"
                        f"📌 Status: Rejected\n"
                        f"🔗 Reference: WR-{withdrawal_request.id}"
                    )
                    requests.post(telegram_url, json={'chat_id': withdrawal_request.user.telegram_id, 'text': text, 'parse_mode': 'HTML'})
            except Exception:
                pass
            
            return JsonResponse({'success': True, 'message': 'Withdrawal request rejected successfully.'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@admin_required
def unwithdrawable_bonuses(request):
    """View to manage unwithdrawable bonuses"""
    # Get users with unwithdrawable bonuses
    users_with_unwithdrawable = User.objects.filter(unwithdrawable_bonus__gt=0).order_by('-unwithdrawable_bonus')
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    if search_query:
        users_with_unwithdrawable = users_with_unwithdrawable.filter(
            username__icontains=search_query
        )
    
    paginator = Paginator(users_with_unwithdrawable, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate total unwithdrawable bonus amount
    total_unwithdrawable = sum(float(user.unwithdrawable_bonus) for user in users_with_unwithdrawable)
    
    context = {
        'users': page_obj,
        'page_title': 'Unwithdrawable Bonuses',
        'page_obj': page_obj,
        'total_unwithdrawable': total_unwithdrawable,
        'search_query': search_query,
    }
    return render(request, 'dashboard/unwithdrawable_bonuses.html', context)


@admin_required
def move_bonus_to_earnings(request, user_id):
    """Move unwithdrawable bonus to total referral earnings"""
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            
            if user.unwithdrawable_bonus <= 0:
                return JsonResponse({'success': False, 'message': 'User has no unwithdrawable bonus.'})
            
            # Move unwithdrawable bonus to total referral earnings
            bonus_amount = user.unwithdrawable_bonus
            user.total_referral_earnings += bonus_amount
            user.unwithdrawable_bonus = 0
            user.save()
            
            # Update wallet
            wallet, created = Wallet.objects.get_or_create(user=user)
            wallet.unwithdrawable_bonus = 0
            wallet.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'Successfully moved {bonus_amount} birr to total referral earnings.'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@admin_required
def approve_referral_bonus(request, bonus_id):
    """Approve a specific referral bonus"""
    if request.method == 'POST':
        try:
            success, message = ReferralService.approve_bonus(bonus_id, request.user)
            return JsonResponse({'success': success, 'message': message})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


# Referral bonus functions removed


# Bulk approve bonuses function removed


# Process Tuesday bonuses function removed


# Referral bonus views removed


@admin_required
def game_settings(request):
    """Game settings page for managing fake player behavior"""
    from game.models import FakePlayerSettings
    
    if request.method == 'POST':
        try:
            settings = FakePlayerSettings.get_solo()
            settings.max_fake_players = int(request.POST.get('max_fake_players', 50))
            settings.calls_before_fake_winner = int(request.POST.get('calls_before_fake_winner', 10))
            # New: configurable threshold for activating fake players
            settings.real_players_threshold = int(request.POST.get('real_players_threshold', settings.real_players_threshold or 10))
            settings.fake_players_can_win = request.POST.get('fake_players_can_win') == 'on'
            settings.save()
            
            messages.success(request, 'Game settings updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating settings: {str(e)}')
    
    settings = FakePlayerSettings.get_solo()
    
    context = {
        'settings': settings,
        'page_title': 'Game Settings'
    }
    return render(request, 'dashboard/game_settings.html', context)




