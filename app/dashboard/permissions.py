from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from .models import Agent


def admin_required(view_func):
    """
    Decorator that requires the user to be an admin.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def support_required(view_func):
    """
    Decorator that requires the user to be support staff or admin.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Check if user is admin or has support permissions
        if not (request.user.is_staff or 
                request.user.groups.filter(name='Support').exists()):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_or_support_required(view_func):
    """
    Decorator that requires the user to be either admin or support staff.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_staff or 
                request.user.groups.filter(name__in=['Support', 'Admin']).exists()):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def superuser_required(view_func):
    """
    Decorator that requires the user to be a superuser.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def has_permission(permission_name):
    """
    Decorator that checks if user has a specific permission.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(permission_name):
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard:index')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def check_user_role(user):
    """
    Helper function to determine user role.
    Returns: 'superuser', 'admin', 'support', or 'user'
    """
    if user.is_superuser:
        return 'superuser'
    elif user.is_staff:
        return 'admin'
    elif user.groups.filter(name='Support').exists():
        return 'support'
    else:
        return 'user'


def user_can_access_resource(user, resource_type):
    """
    Helper function to check if user can access specific resources.
    """
    role = check_user_role(user)
    
    permissions = {
        'superuser': ['users', 'games', 'rooms', 'settings', 'logs', 'reports'],
        'admin': ['users', 'games', 'rooms', 'reports'],
        'support': ['games', 'rooms', 'reports'],
        'user': []
    }
    
    return resource_type in permissions.get(role, [])


def agent_required(view_func):
    """
    Decorator that requires the user to be an authenticated agent.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if agent is logged in via session
        agent_id = request.session.get('agent_id')
        if not agent_id:
            messages.error(request, "Please log in to access the agent dashboard.")
            return redirect('agent:login')
        
        try:
            agent = Agent.objects.get(id=agent_id, is_active=True)
            request.agent = agent  # Add agent to request for easy access
        except Agent.DoesNotExist:
            messages.error(request, "Invalid agent session. Please log in again.")
            return redirect('agent:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def agent_login_required(view_func):
    """
    Decorator that requires agent to be logged in, but allows access to login page.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Allow access to login page
        if request.resolver_match.url_name == 'login':
            return view_func(request, *args, **kwargs)
        
        # Check if agent is logged in
        agent_id = request.session.get('agent_id')
        if not agent_id:
            return redirect('agent:login')
        
        try:
            agent = Agent.objects.get(id=agent_id, is_active=True)
            request.agent = agent
        except Agent.DoesNotExist:
            return redirect('agent:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
