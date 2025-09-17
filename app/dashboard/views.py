from this import d
from datetime import timedelta
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from users.models import User, SupportUser, Referral, Contact
from game.models import Game
from wallet.models import Transaction, WithdrawalRequest, PaymentDepositGatewaySettings, PaymentWithdrawalGatewaySettings, ManualSession
from django.shortcuts import render, redirect
from django.contrib import messages
import json
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
from .tasks import send_message_to_all_players, send_message, broadcast_message_with_progress
from .models import BroadcastMessage

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
    from django.db.models import Q
    from datetime import datetime, timedelta
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    game_type_filter = request.GET.get('game_type', 'all')
    date_filter = request.GET.get('date_range', '30')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    min_stake = request.GET.get('min_stake', '')
    max_stake = request.GET.get('max_stake', '')
    
    # Start with all games
    games = Game.objects.select_related('winner').all().order_by('-created_at')
    
    # Apply search filter
    if search_query:
        games = games.filter(
            Q(id__icontains=search_query) |
            Q(winner__username__icontains=search_query) |
            Q(winner__phone__icontains=search_query) |
            Q(entry_fee__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter != 'all':
        games = games.filter(status=status_filter)
    
    # Apply game type filter (based on entry_fee)
    if game_type_filter != 'all':
        if game_type_filter == 'room_10':
            games = games.filter(entry_fee=10)
        elif game_type_filter == 'room_20':
            games = games.filter(entry_fee=20)
        elif game_type_filter == 'room_30':
            games = games.filter(entry_fee=30)
        elif game_type_filter == 'room_50':
            games = games.filter(entry_fee=50)
    
    # Apply date filters
    if date_filter == 'today':
        games = games.filter(created_at__date=timezone.now().date())
    elif date_filter == '7':
        games = games.filter(created_at__gte=timezone.now() - timedelta(days=7))
    elif date_filter == '30':
        games = games.filter(created_at__gte=timezone.now() - timedelta(days=30))
    elif date_filter == 'custom' and start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            games = games.filter(created_at__date__range=[start_date_obj, end_date_obj])
        except ValueError:
            pass
    
    # Apply stake filters
    if min_stake:
        try:
            games = games.filter(entry_fee__gte=float(min_stake))
        except ValueError:
            pass
    
    if max_stake:
        try:
            games = games.filter(entry_fee__lte=float(max_stake))
        except ValueError:
            pass
    
    # Pagination
    paginator = Paginator(games, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics
    total_games = games.count()
    active_games = games.filter(status="in_progress").count()
    completed_today = games.filter(status="completed", created_at__date=timezone.now().date()).count()
    total_revenue = games.aggregate(Sum('entry_fee'))['entry_fee__sum'] or 0
    
    # Get unique game types for filter dropdown
    game_types = Game.objects.values_list('entry_fee', flat=True).distinct().order_by('entry_fee')
    
    context = {
        'games': page_obj,
        'page_obj': page_obj,
        'page_title': 'Games',
        'total_games': total_games,
        'active_games': active_games,
        'completed_today': completed_today,
        'total_revenue': total_revenue,
        'search_query': search_query,
        'current_status': status_filter,
        'current_game_type': game_type_filter,
        'current_date_range': date_filter,
        'start_date': start_date,
        'end_date': end_date,
        'min_stake': min_stake,
        'max_stake': max_stake,
        'game_types': game_types,
        'status_choices': ['all', 'waiting', 'in_progress', 'completed'],
        'date_choices': [
            ('today', 'Today'),
            ('7', 'Last 7 days'),
            ('30', 'Last 30 days'),
            ('custom', 'Custom range')
        ]
    }
    return render(request, 'dashboard/games.html',context)

def payments(request):
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    deposit_status_filter = request.GET.get('deposit_status', 'all')
    
    # Filter withdrawal requests based on status
    withdrawal_requests = WithdrawalRequest.objects.all().order_by('-created_at')
    
    if status_filter != 'all':
        withdrawal_requests = withdrawal_requests.filter(status=status_filter)
    
    # Filter manual deposits based on status
    manual_deposits = ManualSession.objects.all().order_by('-created_at')
    
    if deposit_status_filter != 'all':
        manual_deposits = manual_deposits.filter(status=deposit_status_filter)
    
    # Pagination for withdrawal requests
    withdrawal_paginator = Paginator(withdrawal_requests, 10)
    withdrawal_page_number = request.GET.get('withdrawal_page')
    withdrawal_page_obj = withdrawal_paginator.get_page(withdrawal_page_number)
    
    # Pagination for manual deposits
    deposit_paginator = Paginator(manual_deposits, 10)
    deposit_page_number = request.GET.get('deposit_page')
    deposit_page_obj = deposit_paginator.get_page(deposit_page_number)
    
    payment_deposit_gateway_settings = PaymentDepositGatewaySettings.objects.first()
    payment_withdrawal_gateway_settings = PaymentWithdrawalGatewaySettings.objects.first()
    
    context = {
        'withdrawal_requests': withdrawal_page_obj,
        'page_title': 'Payments',
        'withdrawal_page_obj': withdrawal_page_obj,
        'deposit_page_obj': deposit_page_obj,
        'current_status': status_filter,
        'current_deposit_status': deposit_status_filter,
        'status_choices': ['all', 'pending', 'success', 'failed'],
        'payment_deposit_gateway_settings': payment_deposit_gateway_settings,
        'payment_withdrawal_gateway_settings': payment_withdrawal_gateway_settings,
        'manual_deposits': deposit_page_obj
    }
    return render(request, 'dashboard/payments.html', context)


def transcations(request):
    from django.db.models import Q
    from datetime import datetime, timedelta
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    transaction_type = request.GET.get('type', 'all')
    status_filter = request.GET.get('status', 'all')
    date_filter = request.GET.get('date_range', '30')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Start with all transactions
    transactions = Transaction.objects.all().order_by('-created_at')
    
    # Apply search filter
    if search_query:
        transactions = transactions.filter(
            Q(user__username__icontains=search_query) |
            Q(user__phone__icontains=search_query) |
            Q(reference__icontains=search_query) |
            Q(amount__icontains=search_query)
        )
    
    # Apply transaction type filter
    if transaction_type != 'all':
        transactions = transactions.filter(type=transaction_type)
    
    # Apply status filter
    if status_filter != 'all':
        transactions = transactions.filter(status=status_filter)
    
    # Apply date filter
    if date_filter == 'today':
        today = timezone.now().date()
        transactions = transactions.filter(created_at__date=today)
    elif date_filter == '7':
        week_ago = timezone.now() - timedelta(days=7)
        transactions = transactions.filter(created_at__gte=week_ago)
    elif date_filter == '30':
        month_ago = timezone.now() - timedelta(days=30)
        transactions = transactions.filter(created_at__gte=month_ago)
    elif date_filter == 'custom' and start_date and end_date:
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            transactions = transactions.filter(
                created_at__date__gte=start_date_obj,
                created_at__date__lte=end_date_obj
            )
        except ValueError:
            pass  # Invalid date format, ignore filter
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate totals based on filtered data
    total_transactions = transactions.count()
    total_in = transactions.filter(type="DEPOSIT").aggregate(Sum('amount'))['amount__sum'] or 0
    total_out = transactions.filter(type="WITHDRAW").aggregate(Sum('amount'))['amount__sum'] or 0
    net = total_in - total_out
    
    has_next = page_obj.has_next()
    has_previous = page_obj.has_previous()
    next_page = page_obj.next_page_number() if has_next else None
    previous_page = page_obj.previous_page_number() if has_previous else None

    context = {
        'transactions': page_obj,
        'page_title': 'Transactions',
        'page_obj': page_obj,
        'total_transactions': total_transactions,
        'total_in': total_in,
        'total_out': total_out,
        'net': net,
        'has_next': has_next,
        'has_previous': has_previous,
        'next_page': next_page,
        'previous_page': previous_page,
        'search_query': search_query,
        'current_type': transaction_type,
        'current_status': status_filter,
        'current_date_range': date_filter,
        'start_date': start_date,
        'end_date': end_date,
        'type_choices': ['all', 'DEPOSIT', 'WITHDRAW', 'BET', 'WIN'],
        'status_choices': ['all', 'pending', 'success', 'failed'],
        'date_choices': [
            ('today', 'Today'),
            ('7', 'Last 7 days'),
            ('30', 'Last 30 days'),
            ('custom', 'Custom range')
        ]
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
    # Get all referrals with pagination
    referrals = Referral.objects.select_related('referrer', 'referred_user').all().order_by('-created_at')
    paginator = Paginator(referrals, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get referral statistics
    total_referrals = referrals.count()
    total_bonus_paid = referrals.filter(bonus_paid=True).aggregate(total=Sum('bonus_amount'))['total'] or 0
    pending_bonuses = referrals.filter(bonus_paid=False).count()
    
    # Get top referrers
    top_referrers = User.objects.annotate(
        referral_count=Count('referrals_made')
    ).filter(referral_count__gt=0).order_by('-referral_count')[:10]
    
    context = {
        'referrals': page_obj,
        'page_obj': page_obj,
        'total_referrals': total_referrals,
        'total_bonus_paid': total_bonus_paid,
        'pending_bonuses': pending_bonuses,
        'top_referrers': top_referrers,
    }
    return render(request, 'dashboard/referrals.html', context)

def messages_view(request):
    # Get broadcast messages with pagination
    broadcasts = BroadcastMessage.objects.all().order_by('-created_at')
    paginator = Paginator(broadcasts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'broadcasts': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'dashboard/messages.html', context)

def contact(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', 'all')
    status_filter = request.GET.get('status', 'all')
    
    # Start with all contacts
    contacts = Contact.objects.all().order_by('-created_at')
    
    # Apply search filter
    if search_query:
        contacts = contacts.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(department__icontains=search_query)
        )
    
    # Apply role filter
    if role_filter != 'all':
        contacts = contacts.filter(role=role_filter)
    
    # Apply status filter
    if status_filter != 'all':
        if status_filter == 'active':
            contacts = contacts.filter(is_active=True)
        elif status_filter == 'inactive':
            contacts = contacts.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(contacts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    total_contacts = contacts.count()
    active_contacts = contacts.filter(is_active=True).count()
    inactive_contacts = contacts.filter(is_active=False).count()
    
    # Get role choices for filter
    role_choices = Contact.ROLE_CHOICES
    
    context = {
        'contacts': page_obj,
        'page_obj': page_obj,
        'total_contacts': total_contacts,
        'active_contacts': active_contacts,
        'inactive_contacts': inactive_contacts,
        'search_query': search_query,
        'current_role': role_filter,
        'current_status': status_filter,
        'role_choices': role_choices,
        'status_choices': [('all', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')]
    }
    return render(request, 'dashboard/contact.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@admin_or_support_required
def contacts_api(request):
    """API endpoint for contact CRUD operations"""
    if request.method == 'POST':
        # Create new contact
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            contact = Contact.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone', ''),
                role=data.get('role'),
                department=data.get('department', 'Operations'),
                is_active=data.get('is_active', True),
                permissions=data.get('permissions', []),
                created_by_id=request.user.id
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Contact created successfully',
                'contact': {
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'role': contact.role,
                    'role_display': contact.role_display,
                    'department': contact.department,
                    'is_active': contact.is_active,
                    'permissions': contact.permissions,
                    'created_at': contact.created_at.isoformat()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    elif request.method == 'GET':
        # Get all contacts with optional filtering
        search_query = request.GET.get('search', '')
        role_filter = request.GET.get('role', 'all')
        status_filter = request.GET.get('status', 'all')
        
        contacts = Contact.objects.all().order_by('-created_at')
        
        if search_query:
            contacts = contacts.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(department__icontains=search_query)
            )
        
        if role_filter != 'all':
            contacts = contacts.filter(role=role_filter)
        
        if status_filter != 'all':
            if status_filter == 'active':
                contacts = contacts.filter(is_active=True)
            elif status_filter == 'inactive':
                contacts = contacts.filter(is_active=False)
        
        contacts_data = []
        for contact in contacts:
            contacts_data.append({
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'role': contact.role,
                'role_display': contact.role_display,
                'department': contact.department,
                'is_active': contact.is_active,
                'permissions': contact.permissions,
                'created_at': contact.created_at.isoformat(),
                'updated_at': contact.updated_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'contacts': contacts_data,
            'total': contacts.count()
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@admin_or_support_required
def contact_detail_api(request, contact_id):
    """API endpoint for individual contact operations"""
    try:
        contact = Contact.objects.get(id=contact_id)
    except Contact.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Contact not found'})
    
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'contact': {
                'id': contact.id,
                'name': contact.name,
                'email': contact.email,
                'phone': contact.phone,
                'role': contact.role,
                'role_display': contact.role_display,
                'department': contact.department,
                'is_active': contact.is_active,
                'permissions': contact.permissions,
                'created_at': contact.created_at.isoformat(),
                'updated_at': contact.updated_at.isoformat(),
                'created_by': contact.created_by.username if contact.created_by else 'System'
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            contact.name = data.get('name', contact.name)
            contact.email = data.get('email', contact.email)
            contact.phone = data.get('phone', contact.phone)
            contact.role = data.get('role', contact.role)
            contact.department = data.get('department', contact.department)
            contact.is_active = data.get('is_active', contact.is_active)
            contact.permissions = data.get('permissions', contact.permissions)
            contact.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Contact updated successfully',
                'contact': {
                    'id': contact.id,
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'role': contact.role,
                    'role_display': contact.role_display,
                    'department': contact.department,
                    'is_active': contact.is_active,
                    'permissions': contact.permissions,
                    'updated_at': contact.updated_at.isoformat()
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    elif request.method == 'DELETE':
        contact.delete()
        return JsonResponse({
            'success': True,
            'message': 'Contact deleted successfully'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@admin_or_support_required
def toggle_contact_status_api(request, contact_id):
    """API endpoint to toggle contact active status"""
    if request.method == 'POST':
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.is_active = not contact.is_active
            contact.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Contact {"activated" if contact.is_active else "deactivated"} successfully',
                'is_active': contact.is_active
            })
            
        except Contact.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Contact not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

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

            # notify telegram user
            send_message(withdrawal_request.user.telegram_id, f"Your withdrawal request has been approved. Amount: {withdrawal_request.amount} ETB")
            
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
            
            # Get rejection reason from request body
            data = json.loads(request.body.decode('utf-8'))
            rejection_reason = data.get('rejection_reason', '')
            
            # Update withdrawal request status and reason
            withdrawal_request.status = 'failed'
            withdrawal_request.rejection_reason = rejection_reason
            withdrawal_request.save()

            # notify telegram user
            send_message(withdrawal_request.user.telegram_id, f"Your withdrawal request has been rejected. Reason: {rejection_reason}")
            
            return JsonResponse({'success': True, 'message': 'Withdrawal request rejected successfully.'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@admin_or_support_required
def broadcast_message_api(request):
    """API endpoint to start broadcasting a message"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'success': False, 'message': 'Message cannot be empty'})
            
            # Create broadcast message record
            broadcast = BroadcastMessage.objects.create(
                message=message,
                created_by_id=request.user.id,
                status='pending'
            )
            
            # Start the broadcast task
            broadcast_message_with_progress.delay(broadcast.id)
            
            return JsonResponse({
                'success': True, 
                'message': 'Broadcast started successfully',
                'broadcast_id': broadcast.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@admin_or_support_required
def message_progress_api(request, broadcast_id):
    """API endpoint to get broadcast progress"""
    if request.method == 'GET':
        try:
            broadcast = BroadcastMessage.objects.get(id=broadcast_id)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': broadcast.id,
                    'message': broadcast.message,
                    'status': broadcast.status,
                    'total_recipients': broadcast.total_recipients,
                    'sent_count': broadcast.sent_count,
                    'failed_count': broadcast.failed_count,
                    'progress_percentage': broadcast.progress_percentage,
                    'created_at': broadcast.created_at.isoformat(),
                    'completed_at': broadcast.completed_at.isoformat() if broadcast.completed_at else None,
                    'error_message': broadcast.error_message
                }
            })
            
        except BroadcastMessage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Broadcast not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@admin_or_support_required
def broadcast_details_api(request, broadcast_id):
    """API endpoint to get detailed broadcast information"""
    if request.method == 'GET':
        try:
            broadcast = BroadcastMessage.objects.get(id=broadcast_id)
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': broadcast.id,
                    'message': broadcast.message,
                    'status': broadcast.status,
                    'total_recipients': broadcast.total_recipients,
                    'sent_count': broadcast.sent_count,
                    'failed_count': broadcast.failed_count,
                    'progress_percentage': broadcast.progress_percentage,
                    'created_at': broadcast.created_at.isoformat(),
                    'completed_at': broadcast.completed_at.isoformat() if broadcast.completed_at else None,
                    'created_by': broadcast.created_by.username if broadcast.created_by else 'System',
                    'error_message': broadcast.error_message
                }
            })
            
        except BroadcastMessage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Broadcast not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@admin_or_support_required
def resend_broadcast_api(request, broadcast_id):
    """API endpoint to resend a completed broadcast"""
    if request.method == 'POST':
        try:
            broadcast = BroadcastMessage.objects.get(id=broadcast_id)
            
            if broadcast.status != 'completed':
                return JsonResponse({'success': False, 'message': 'Only completed broadcasts can be resent'})
            
            # Create a new broadcast with the same message
            new_broadcast = BroadcastMessage.objects.create(
                message=broadcast.message,
                created_by_id=request.user.id,
                status='pending'
            )
            
            # Start the new broadcast task
            broadcast_message_with_progress.delay(new_broadcast.id)
            
            return JsonResponse({
                'success': True, 
                'message': 'Broadcast resend started successfully',
                'broadcast_id': new_broadcast.id
            })
            
        except BroadcastMessage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Broadcast not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@admin_or_support_required
def cancel_broadcast_api(request, broadcast_id):
    """API endpoint to cancel a pending or sending broadcast"""
    if request.method == 'POST':
        try:
            broadcast = BroadcastMessage.objects.get(id=broadcast_id)
            
            if broadcast.status not in ['pending', 'sending']:
                return JsonResponse({'success': False, 'message': 'Only pending or sending broadcasts can be cancelled'})
            
            # Update status to cancelled
            broadcast.status = 'cancelled'
            broadcast.completed_at = timezone.now()
            broadcast.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Broadcast cancelled successfully'
            })
            
        except BroadcastMessage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Broadcast not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


