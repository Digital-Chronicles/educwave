from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles=None, redirect_url=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            if redirect_url:
                return redirect(redirect_url)
            
            raise PermissionDenied
        
        return wrapper

    return decorator
