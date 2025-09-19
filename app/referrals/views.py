from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from decimal import Decimal
from .models import ReferralBonus, ReferralWithdrawal, UserGameStats, ReferralSettings
from .services import ReferralService
import json

@login_required
def referrals_dashboard(request):
    """Main referrals dashboard"""
    user = request.user
    
    # Get user stats
    stats, created = UserGameStats.objects.get_or_create(user=user)
    available_balance = ReferralService.get_available_referral_balance(user)
    can_withdraw = ReferralService.can_withdraw_referral_bonus(user)
    
    # Get recent bonuses
    recent_bonuses = ReferralBonus.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Get recent withdrawals
    recent_withdrawals = ReferralWithdrawal.objects.filter(user=user).order_by('-created_at')[:10]
    
    # Get referral tree
    try:
        referral_tree = ReferralService.get_referral_tree(user)
    except Exception as e:
        referral_tree = []
    
    # Get settings
    settings = ReferralSettings.get_settings()
    
    context = {
        'user': user,
        'stats': stats,
        'available_balance': available_balance,
        'can_withdraw': can_withdraw,
        'recent_bonuses': recent_bonuses,
        'recent_withdrawals': recent_withdrawals,
        'referral_tree': referral_tree,
        'settings': settings,
    }
    
    return render(request, 'referrals/dashboard.html', context)

@login_required
def referral_bonuses(request):
    """View all referral bonuses"""
    bonuses = ReferralBonus.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'bonuses': bonuses,
    }
    
    return render(request, 'referrals/bonuses.html', context)

@login_required
def withdrawal_requests(request):
    """View withdrawal requests"""
    withdrawals = ReferralWithdrawal.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'withdrawals': withdrawals,
    }
    
    return render(request, 'referrals/withdrawals.html', context)

@login_required
@require_http_methods(["POST"])
def request_withdrawal(request):
    """Handle withdrawal request"""
    try:
        data = json.loads(request.body)
        amount = Decimal(str(data.get('amount', 0)))
        
        success, result = ReferralService.request_withdrawal(request.user, amount)
        
        if success:
            messages.success(request, f'Withdrawal request of {amount} birr submitted successfully')
            return JsonResponse({'success': True, 'message': 'Withdrawal request submitted successfully'})
        else:
            messages.error(request, result)
            return JsonResponse({'success': False, 'error': result})
            
    except Exception as e:
        messages.error(request, 'Invalid request')
        return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
@require_http_methods(["POST"])
def change_sponsor(request):
    """Handle sponsor change request"""
    try:
        data = json.loads(request.body)
        sponsor_code = data.get('sponsor_code', '').strip()
        
        if not sponsor_code:
            return JsonResponse({'success': False, 'error': 'Sponsor code is required'})
        
        if request.user.sponsor_changed:
            return JsonResponse({'success': False, 'error': 'You can only change sponsor once'})
        
        from users.models import User
        try:
            sponsor = User.objects.get(referral_code=sponsor_code)
            if sponsor == request.user:
                return JsonResponse({'success': False, 'error': 'Cannot be your own sponsor'})
            
            request.user.sponsor = sponsor
            request.user.is_agent = False
            request.user.sponsor_changed = True
            request.user.save()
            
            messages.success(request, 'Sponsor changed successfully')
            return JsonResponse({'success': True, 'message': 'Sponsor changed successfully'})
            
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid sponsor code'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def referral_tree(request):
    """View referral tree"""
    tree = ReferralService.get_referral_tree(request.user)
    
    context = {
        'referral_tree': tree,
    }
    
    return render(request, 'referrals/tree.html', context)