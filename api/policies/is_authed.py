from api.services.auth_service import get_authed_user

def is_authed(func):
    def decorator(*args, **kwargs):
        get_authed_user()
        return func(*args, **kwargs)
    return decorator
