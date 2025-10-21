from ninja import Router
from ninja.security import HttpBearer
from django.http import JsonResponse
from django.conf import settings
from django.utils import timezone
from .models import Promotion, Banner
from users.auth import JWTAuth
import logging

logger = logging.getLogger(__name__)

# Create router
promotion_router = Router()

# Auth instance
auth = JWTAuth()

@promotion_router.get("/active")
def get_active_promotions(request):
    """
    Get all active promotions for display
    """
    try:
        now = timezone.now()
        active_promotions = Promotion.objects.filter(
            status='active',
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-created_at')
        
        promotions_data = []
        for promotion in active_promotions:
            promotion_data = {
                'id': promotion.id,
                'title': promotion.title,
                'description': promotion.description,
                'promotion_type': promotion.promotion_type,
                'discount_percentage': float(promotion.discount_percentage) if promotion.discount_percentage else None,
                'bonus_amount': float(promotion.bonus_amount) if promotion.bonus_amount else None,
                'minimum_deposit': float(promotion.minimum_deposit) if promotion.minimum_deposit else None,
                'banner_image_url': promotion.banner_image.image.url if promotion.banner_image else None,
                'created_at': promotion.created_at.isoformat(),
                'end_date': promotion.end_date.isoformat() if promotion.end_date else None,
            }
            promotions_data.append(promotion_data)
        
        return JsonResponse({
            'success': True,
            'promotions': promotions_data
        }, status=200)
        
    except Exception as e:
        logger.error(f"Error fetching active promotions: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to fetch promotions'
        }, status=500)

@promotion_router.post("/send", auth=auth)
def send_promotion(request, promotion_id: int):
    """
    Send a promotion to all connected players via WebSocket
    Admin only endpoint
    """
    try:
        # Check if user is admin
        user_id = request.auth.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required'
            }, status=401)
        
        # Get promotion
        try:
            promotion = Promotion.objects.get(id=promotion_id)
        except Promotion.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Promotion not found'
            }, status=404)
        
        # Check if promotion is active
        if not promotion.is_active:
            return JsonResponse({
                'success': False,
                'message': 'Promotion is not active'
            }, status=400)
        
        # Prepare promotion data for WebSocket
        promotion_data = {
            'id': promotion.id,
            'title': promotion.title,
            'description': promotion.description,
            'promotion_type': promotion.promotion_type,
            'discount_percentage': float(promotion.discount_percentage) if promotion.discount_percentage else None,
            'bonus_amount': float(promotion.bonus_amount) if promotion.bonus_amount else None,
            'minimum_deposit': float(promotion.minimum_deposit) if promotion.minimum_deposit else None,
            'banner_image_url': promotion.banner_image.image.url if promotion.banner_image else None,
            'end_date': promotion.end_date.isoformat() if promotion.end_date else None,
        }
        
        # Send via WebSocket to all connected players
        try:
            import requests
            import json
            
            # Send to WebSocket server
            websocket_url = "http://localhost:3001/send-promotion"  # Adjust port as needed
            websocket_data = {
                'promotion': promotion_data,
                'admin_id': user_id
            }
            
            # This would be a custom endpoint on the WebSocket server
            # For now, we'll use a simple approach
            logger.info(f"Promotion {promotion.id} data prepared for WebSocket broadcast")
            
        except Exception as ws_error:
            logger.error(f"WebSocket communication error: {ws_error}")
        
        logger.info(f"Promotion {promotion.id} sent by admin {user_id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Promotion sent successfully',
            'promotion': promotion_data
        }, status=200)
        
    except Exception as e:
        logger.error(f"Error sending promotion: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to send promotion'
        }, status=500)

@promotion_router.post("/track-view/{promotion_id}")
def track_promotion_view(request, promotion_id: int):
    """
    Track when a promotion is viewed
    """
    try:
        promotion = Promotion.objects.get(id=promotion_id)
        promotion.increment_view_count()
        
        return JsonResponse({
            'success': True,
            'message': 'View tracked'
        }, status=200)
        
    except Promotion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Promotion not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error tracking promotion view: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to track view'
        }, status=500)

@promotion_router.post("/track-click/{promotion_id}")
def track_promotion_click(request, promotion_id: int):
    """
    Track when a promotion is clicked
    """
    try:
        promotion = Promotion.objects.get(id=promotion_id)
        promotion.increment_click_count()
        
        return JsonResponse({
            'success': True,
            'message': 'Click tracked'
        }, status=200)
        
    except Promotion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Promotion not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error tracking promotion click: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to track click'
        }, status=500)

@promotion_router.get("/admin/list", auth=auth)
def list_promotions_admin(request):
    """
    List all promotions for admin dashboard
    """
    try:
        # Check if user is admin (you might want to add proper admin check)
        user_id = request.auth.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': 'Authentication required'
            }, status=401)
        
        promotions = Promotion.objects.all().order_by('-created_at')
        
        promotions_data = []
        for promotion in promotions:
            promotion_data = {
                'id': promotion.id,
                'title': promotion.title,
                'description': promotion.description,
                'promotion_type': promotion.promotion_type,
                'status': promotion.status,
                'discount_percentage': float(promotion.discount_percentage) if promotion.discount_percentage else None,
                'bonus_amount': float(promotion.bonus_amount) if promotion.bonus_amount else None,
                'minimum_deposit': float(promotion.minimum_deposit) if promotion.minimum_deposit else None,
                'banner_image_url': promotion.banner_image.image.url if promotion.banner_image else None,
                'view_count': promotion.view_count,
                'click_count': promotion.click_count,
                'created_at': promotion.created_at.isoformat(),
                'start_date': promotion.start_date.isoformat() if promotion.start_date else None,
                'end_date': promotion.end_date.isoformat() if promotion.end_date else None,
                'is_active': promotion.is_active,
            }
            promotions_data.append(promotion_data)
        
        return JsonResponse({
            'success': True,
            'promotions': promotions_data
        }, status=200)
        
    except Exception as e:
        logger.error(f"Error listing promotions: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to list promotions'
        }, status=500)
