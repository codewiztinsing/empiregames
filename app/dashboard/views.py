from this import d
from datetime import timedelta
from django.db.models import Sum
from django.core.paginator import Paginator
from django.utils import timezone
from users.models import User, SupportUser
from game.models import Game
from wallet.models import Transaction, WithdrawalRequest, PaymentDepositGatewaySettings, PaymentWithdrawalGatewaySettings, ManualSession
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
    games = Game.objects.all().order_by('-id')
    paginator = Paginator(games, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_games = games.count()
    active_games = games.filter(status="active").count()
    completed_today = games.filter(status="completed",created_at__date=timezone.now().date()).count()
    total_revenue = games.aggregate(Sum('entry_fee'))['entry_fee__sum'] or 0
    context = {
        'games': page_obj,
        'page_title': 'Games',
        'page_obj': page_obj,
        'total_games': total_games,
        'active_games': active_games,
        'completed_today': completed_today,
        'total_revenue': total_revenue
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
    transactions = Transaction.objects.all()
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    total_transactions = transactions.count()
    total_in = transactions.filter(type="DEPOSIT").aggregate(Sum('amount'))['amount__sum'] or 0
    total_out = transactions.filter(type="WITHDRAW").aggregate(Sum('amount'))['amount__sum'] or 0
    net = total_in - total_out
    
    
    context = {
        'transactions': page_obj,
        'page_title': 'Transactions',
        'page_obj': page_obj,
        'total_transactions': total_transactions,
        'total_in': total_in,
        'total_out': total_out,
        'net': net
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
    return render(request, 'dashboard/referrals.html')

def messages_view(request):
  
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



