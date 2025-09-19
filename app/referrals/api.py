from ninja import Router
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from users.models import User
from .models import ReferralBonus, ReferralWithdrawal, UserGameStats, ReferralSettings

referral_router = Router()


@referral_router.get("/referrals/stats/")
def get_referral_stats(request):
    """Get comprehensive referral system statistics"""
    try:
        # Get referral settings
        settings = ReferralSettings.get_settings()
        
        # Get total users with referrals
        total_users_with_referrals = User.objects.filter(referred_by__isnull=False).count()
        total_referrers = User.objects.filter(referrals__isnull=False).distinct().count()
        
        # Get referral bonus statistics
        total_bonuses_paid = ReferralBonus.objects.filter(status='paid').aggregate(Sum('bonus_amount'))['bonus_amount__sum'] or 0
        total_bonuses_pending = ReferralBonus.objects.filter(status='pending').aggregate(Sum('bonus_amount'))['bonus_amount__sum'] or 0
        total_bonuses_approved = ReferralBonus.objects.filter(status='approved').aggregate(Sum('bonus_amount'))['bonus_amount__sum'] or 0
        
        # Get withdrawal statistics
        total_withdrawals_pending = ReferralWithdrawal.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        total_withdrawals_approved = ReferralWithdrawal.objects.filter(status='approved').aggregate(Sum('amount'))['amount__sum'] or 0
        total_withdrawals_paid = ReferralWithdrawal.objects.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_bonuses = ReferralBonus.objects.filter(created_at__gte=thirty_days_ago).count()
        recent_withdrawals = ReferralWithdrawal.objects.filter(created_at__gte=thirty_days_ago).count()
        
        return JsonResponse({
            "settings": {
                "first_generation_bonus": float(settings.first_generation_bonus),
                "second_generation_bonus": float(settings.second_generation_bonus),
                "minimum_withdrawal": float(settings.minimum_withdrawal),
                "daily_games_required": settings.daily_games_required,
                "weekly_games_required": settings.weekly_games_required,
                "is_active": settings.is_active
            },
            "statistics": {
                "total_users_with_referrals": total_users_with_referrals,
                "total_referrers": total_referrers,
                "total_bonuses_paid": float(total_bonuses_paid),
                "total_bonuses_pending": float(total_bonuses_pending),
                "total_bonuses_approved": float(total_bonuses_approved),
                "total_withdrawals_pending": float(total_withdrawals_pending),
                "total_withdrawals_approved": float(total_withdrawals_approved),
                "total_withdrawals_paid": float(total_withdrawals_paid),
                "recent_bonuses": recent_bonuses,
                "recent_withdrawals": recent_withdrawals
            }
        }, status=200)
    except Exception as e:
        print(f"Error getting referral stats: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@referral_router.get("/referrals/bonuses/")
def get_referral_bonuses(request, limit: int = 20, status: str = None):
    """Get referral bonuses with optional filtering"""
    try:
        bonuses = ReferralBonus.objects.select_related('user', 'from_user').order_by('-created_at')
        
        if status:
            bonuses = bonuses.filter(status=status)
        
        bonuses = bonuses[:limit]
        
        bonuses_list = []
        for bonus in bonuses:
            bonuses_list.append({
                "id": bonus.id,
                "user": {
                    "id": bonus.user.id,
                    "username": bonus.user.username,
                    "phone": bonus.user.phone,
                    "telegram_id": bonus.user.telegram_id
                },
                "from_user": {
                    "id": bonus.from_user.id,
                    "username": bonus.from_user.username,
                    "phone": bonus.from_user.phone,
                    "telegram_id": bonus.from_user.telegram_id
                },
                "generation": bonus.generation,
                "win_amount": float(bonus.win_amount),
                "bonus_percentage": float(bonus.bonus_percentage),
                "bonus_amount": float(bonus.bonus_amount),
                "game_id": bonus.game_id,
                "status": bonus.status,
                "created_at": bonus.created_at.isoformat()
            })
        
        return JsonResponse({
            "bonuses": bonuses_list,
            "count": len(bonuses_list),
            "status": status or "all"
        }, status=200)
    except Exception as e:
        print(f"Error getting referral bonuses: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@referral_router.get("/referrals/withdrawals/")
def get_referral_withdrawals(request, limit: int = 20, status: str = None):
    """Get referral withdrawal requests with optional filtering"""
    try:
        withdrawals = ReferralWithdrawal.objects.select_related('user').order_by('-created_at')
        
        if status:
            withdrawals = withdrawals.filter(status=status)
        
        withdrawals = withdrawals[:limit]
        
        withdrawals_list = []
        for withdrawal in withdrawals:
            withdrawals_list.append({
                "id": withdrawal.id,
                "user": {
                    "id": withdrawal.user.id,
                    "username": withdrawal.user.username,
                    "phone": withdrawal.user.phone,
                    "telegram_id": withdrawal.user.telegram_id
                },
                "amount": float(withdrawal.amount),
                "status": withdrawal.status,
                "notes": withdrawal.notes,
                "created_at": withdrawal.created_at.isoformat(),
                "processed_at": withdrawal.processed_at.isoformat() if withdrawal.processed_at else None
            })
        
        return JsonResponse({
            "withdrawals": withdrawals_list,
            "count": len(withdrawals_list),
            "status": status or "all"
        }, status=200)
    except Exception as e:
        print(f"Error getting referral withdrawals: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@referral_router.post("/referrals/bonuses/{bonus_id}/approve/")
def approve_referral_bonus(request, bonus_id: int):
    """Approve a referral bonus"""
    try:
        bonus = ReferralBonus.objects.get(id=bonus_id)
        bonus.status = 'approved'
        bonus.save()
        
        return JsonResponse({
            "success": True,
            "message": "Referral bonus approved successfully"
        }, status=200)
    except ReferralBonus.DoesNotExist:
        return JsonResponse({"error": "Referral bonus not found"}, status=404)
    except Exception as e:
        print(f"Error approving referral bonus: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@referral_router.post("/referrals/bonuses/{bonus_id}/reject/")
def reject_referral_bonus(request, bonus_id: int):
    """Reject a referral bonus"""
    try:
        bonus = ReferralBonus.objects.get(id=bonus_id)
        bonus.status = 'rejected'
        bonus.save()
        
        return JsonResponse({
            "success": True,
            "message": "Referral bonus rejected successfully"
        }, status=200)
    except ReferralBonus.DoesNotExist:
        return JsonResponse({"error": "Referral bonus not found"}, status=404)
    except Exception as e:
        print(f"Error rejecting referral bonus: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@referral_router.post("/referrals/withdrawals/{withdrawal_id}/approve/")
def approve_referral_withdrawal(request, withdrawal_id: int):
    """Approve a referral withdrawal request"""
    try:
        withdrawal = ReferralWithdrawal.objects.get(id=withdrawal_id)
        withdrawal.status = 'approved'
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        return JsonResponse({
            "success": True,
            "message": "Referral withdrawal approved successfully"
        }, status=200)
    except ReferralWithdrawal.DoesNotExist:
        return JsonResponse({"error": "Referral withdrawal not found"}, status=404)
    except Exception as e:
        print(f"Error approving referral withdrawal: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@referral_router.post("/referrals/withdrawals/{withdrawal_id}/reject/")
def reject_referral_withdrawal(request, withdrawal_id: int):
    """Reject a referral withdrawal request"""
    try:
        withdrawal = ReferralWithdrawal.objects.get(id=withdrawal_id)
        withdrawal.status = 'rejected'
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        return JsonResponse({
            "success": True,
            "message": "Referral withdrawal rejected successfully"
        }, status=200)
    except ReferralWithdrawal.DoesNotExist:
        return JsonResponse({"error": "Referral withdrawal not found"}, status=404)
    except Exception as e:
        print(f"Error rejecting referral withdrawal: {e}")
        return JsonResponse({"error": str(e)}, status=500)