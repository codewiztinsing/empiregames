from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorator that requires the user to be an admin.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:dashboard')
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
            return redirect('dashboard:dashboard')
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
                request.user.groups.filter(name__in=['Support', 'Admin', 'Finance']).exists()):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:dashboard')
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
            return redirect('dashboard:dashboard')
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
                return redirect('dashboard:dashboard')
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
        'superuser': ['users', 'games', 'rooms', 'settings', 'logs', 'reports', 'payments'],
        'admin': ['users', 'games', 'rooms', 'reports', 'payments'],
        'support': ['games', 'rooms', 'reports'],
        'finance': ['payments'],
        'user': []
    }
    
    return resource_type in permissions.get(role, [])


def roles_required(*roles):
    """
    Decorator that requires the user to have any of the specified roles.
    Roles map to Django groups by name; special roles: 'admin' uses is_staff, 'superuser' uses is_superuser.
    """
    normalized = [r.lower() for r in roles]
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            has_role = False
            if 'superuser' in normalized and user.is_superuser:
                has_role = True
            if 'admin' in normalized and user.is_staff:
                has_role = True
            if any(user.groups.filter(name__iexact=r).exists() for r in roles):
                has_role = True
            if not has_role:
                messages.error(request, "You don't have permission to perform this action.")
                return redirect('dashboard:dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
