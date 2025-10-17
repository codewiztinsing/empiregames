from ninja import Router
from ninja.security import django_auth
from django.shortcuts import get_object_or_404
from decimal import Decimal
from typing import List
from pydantic import BaseModel
from .models import User, ReferralBonus, ReferralAnnouncement
from referrals.models import ReferralWithdrawal as WithdrawalRequest
from .referral_services import ReferralService
from wallet.models import Wallet

router = Router()


class ReferralCodeRequest(BaseModel):
    referral_code: str


class SetReferrerResponse(BaseModel):
    success: bool
    message: str


class ReferralStatsResponse(BaseModel):
    total_referrals: int
    total_second_gen: int
    total_earnings: Decimal
    pending_bonuses: Decimal
    games_played_today: int
    games_played_this_week: int
    can_withdraw: bool
    referral_code: str


class WithdrawalRequestData(BaseModel):
    amount: Decimal


class WithdrawalRequestResponse(BaseModel):
    success: bool
    message: str
    request_id: int = None


class BonusResponse(BaseModel):
    id: int
    referrer: str
    winner: str
    win_amount: Decimal
    bonus_type: str
    bonus_amount: Decimal
    generation_level: int
    status: str
    created_at: str


class WithdrawalResponse(BaseModel):
    id: int
    user: str
    amount: Decimal
    status: str
    created_at: str
    processed_at: str = None


class AnnouncementResponse(BaseModel):
    id: int
    title: str
    message: str
    is_active: bool
    created_at: str


@router.post("/set-referrer", response=SetReferrerResponse)
def set_referrer(request, data: ReferralCodeRequest):
    """Set referrer using referral code"""
    if not request.user.is_authenticated:
        return SetReferrerResponse(success=False, message="Authentication required")
    
    success, message = ReferralService.set_referrer(request.user, data.referral_code)
    return SetReferrerResponse(success=success, message=message)


@router.get("/stats", response=ReferralStatsResponse)
def get_referral_stats(request):
    """Get user's referral statistics"""
    # For now, return default stats for anonymous users
    # In production, this should be properly authenticated
    if not request.user.is_authenticated:
        return ReferralStatsResponse(
            total_referrals=0,
            total_second_gen=0,
            total_earnings=Decimal('0.00'),
            pending_bonuses=Decimal('0.00'),
            games_played_today=0,
            games_played_this_week=0,
            can_withdraw=False,
            referral_code="DEMO123"
        )
    
    stats = ReferralService.get_referral_stats(request.user)
    stats['referral_code'] = request.user.referral_code
    return ReferralStatsResponse(**stats)


@router.get("/bonuses", response=List[BonusResponse])
def get_referral_bonuses(request):
    """Get user's referral bonuses"""
    if not request.user.is_authenticated:
        return []
    
    bonuses = ReferralBonus.objects.filter(referrer=request.user).order_by('-created_at')
    return [
        BonusResponse(
            id=bonus.id,
            referrer=bonus.referrer.username,
            winner=bonus.winner.username,
            win_amount=bonus.win_amount,
            bonus_type=bonus.bonus_type,
            bonus_amount=bonus.bonus_amount,
            generation_level=bonus.generation_level,
            status=bonus.status,
            created_at=bonus.created_at.isoformat()
        )
        for bonus in bonuses
    ]


@router.post("/withdrawal-request", response=WithdrawalRequestResponse)
def create_withdrawal_request(request, data: WithdrawalRequestData):
    """Create a withdrawal request"""
    if not request.user.is_authenticated:
        return WithdrawalRequestResponse(success=False, message="Authentication required")
    
    success, message = ReferralService.create_withdrawal_request(request.user, data.amount)
    
    if success:
        withdrawal = WithdrawalRequest.objects.filter(
            user=request.user, 
            status='pending'
        ).latest('created_at')
        return WithdrawalRequestResponse(
            success=True, 
            message=message, 
            request_id=withdrawal.id
        )
    
    return WithdrawalRequestResponse(success=False, message=message)


@router.get("/withdrawals", response=List[WithdrawalResponse])
def get_withdrawal_requests(request):
    """Get user's withdrawal requests"""
    if not request.user.is_authenticated:
        return []
    
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-created_at')
    return [
        WithdrawalResponse(
            id=withdrawal.id,
            user=withdrawal.user.username,
            amount=withdrawal.amount,
            status=withdrawal.status,
            created_at=withdrawal.created_at.isoformat(),
            processed_at=withdrawal.processed_at.isoformat() if withdrawal.processed_at else None
        )
        for withdrawal in withdrawals
    ]


@router.get("/announcements", response=List[AnnouncementResponse])
def get_announcements(request):
    """Get active referral announcements"""
    announcements = ReferralAnnouncement.objects.filter(is_active=True).order_by('-created_at')
    return [
        AnnouncementResponse(
            id=announcement.id,
            title=announcement.title,
            message=announcement.message,
            is_active=announcement.is_active,
            created_at=announcement.created_at.isoformat()
        )
        for announcement in announcements
    ]


# Admin endpoints
@router.get("/admin/bonuses", response=List[BonusResponse], auth=django_auth)
def get_all_bonuses(request):
    """Get all referral bonuses (admin only)"""
    if not request.user.is_staff:
        return []
    
    bonuses = ReferralBonus.objects.all().order_by('-created_at')
    return [
        BonusResponse(
            id=bonus.id,
            referrer=bonus.referrer.username,
            winner=bonus.winner.username,
            win_amount=bonus.win_amount,
            bonus_type=bonus.bonus_type,
            bonus_amount=bonus.bonus_amount,
            generation_level=bonus.generation_level,
            status=bonus.status,
            created_at=bonus.created_at.isoformat()
        )
        for bonus in bonuses
    ]


@router.post("/admin/bonuses/{bonus_id}/approve", response=SetReferrerResponse, auth=django_auth)
def approve_bonus(request, bonus_id: int):
    """Approve a referral bonus (admin only)"""
    if not request.user.is_staff:
        return SetReferrerResponse(success=False, message="Unauthorized")
    
    success, message = ReferralService.approve_bonus(bonus_id, request.user)
    return SetReferrerResponse(success=success, message=message)


@router.get("/admin/withdrawals", response=List[WithdrawalResponse], auth=django_auth)
def get_all_withdrawals(request):
    """Get all withdrawal requests (admin only)"""
    if not request.user.is_staff:
        return []
    
    withdrawals = WithdrawalRequest.objects.all().order_by('-created_at')
    return [
        WithdrawalResponse(
            id=withdrawal.id,
            user=withdrawal.user.username,
            amount=withdrawal.amount,
            status=withdrawal.status,
            created_at=withdrawal.created_at.isoformat(),
            processed_at=withdrawal.processed_at.isoformat() if withdrawal.processed_at else None
        )
        for withdrawal in withdrawals
    ]


@router.post("/admin/withdrawals/{withdrawal_id}/approve", response=SetReferrerResponse, auth=django_auth)
def approve_withdrawal(request, withdrawal_id: int):
    """Approve a withdrawal request (admin only)"""
    if not request.user.is_staff:
        return SetReferrerResponse(success=False, message="Unauthorized")
    
    try:
        withdrawal = WithdrawalRequest.objects.get(id=withdrawal_id, status='pending')
        withdrawal.status = 'approved'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        return SetReferrerResponse(success=True, message="Withdrawal approved")
    except WithdrawalRequest.DoesNotExist:
        return SetReferrerResponse(success=False, message="Withdrawal not found")


@router.post("/admin/withdrawals/{withdrawal_id}/reject", response=SetReferrerResponse, auth=django_auth)
def reject_withdrawal(request, withdrawal_id: int):
    """Reject a withdrawal request (admin only)"""
    if not request.user.is_staff:
        return SetReferrerResponse(success=False, message="Unauthorized")
    
    try:
        withdrawal = WithdrawalRequest.objects.get(id=withdrawal_id, status='pending')
        withdrawal.status = 'rejected'
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save()
        
        return SetReferrerResponse(success=True, message="Withdrawal rejected")
    except WithdrawalRequest.DoesNotExist:
        return SetReferrerResponse(success=False, message="Withdrawal not found")
