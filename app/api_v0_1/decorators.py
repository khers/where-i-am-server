from functools import wraps
from flask import g
from .errors import forbidden

def authentication_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.current_user.is_anonymous:
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
