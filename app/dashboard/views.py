from this import d
from datetime import timedelta
from django.db.models import Sum
from django.core.paginator import Paginator
from django.utils import timezone
from users.models import User
from game.models import Game
from wallet.models import Transaction
from django.shortcuts import render, redirect
from django.contrib import messages
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
    context = {
        'games': page_obj,
        'page_title': 'Games',
        'page_obj': page_obj
    }
    return render(request, 'dashboard/games.html',context)

def payments(request):
    return render(request, 'dashboard/payments.html')


def transcations(request):
    return render(request, 'dashboard/transcations.html')

def users(request):
    return render(request, 'dashboard/users.html')


def bingo_cards(request):
    return render(request, 'dashboard/bingo_cards.html')

def referrals(request):
    return render(request, 'dashboard/referrals.html')

def messages(request):
    return render(request, 'dashboard/messages.html')

def contact(request):
    return render(request, 'dashboard/contact.html')

def logout(request):
    return render(request, 'dashboard/logout.html')



