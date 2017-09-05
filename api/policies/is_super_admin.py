from api.services.auth_service import get_authed_user
from api.exceptions.auth_exceptions import RoleInvalid

def is_super_admin(func):
    def decorator(*args, **kwargs):
        authed_user = get_authed_user()
        if not authed_user.role or authed_user.role != 'super_admin':
            raise RoleInvalid('super_admin')
        return func(*args, **kwargs)
    return decorator
