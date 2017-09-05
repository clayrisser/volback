from nails.exceptions import Unauthorized, BadRequest

class TokenInvalid(Unauthorized):
    def __init__(self):
        self.message = 'Token invalid'
        Unauthorized.__init__(self)

class TokenExpired(Unauthorized):
    def __init__(self):
        self.message = 'Token expired'
        Unauthorized.__init__(self)

class LoggedOut(Unauthorized):
    def __init__(self):
        self.message = 'Not logged in'
        Unauthorized.__init__(self)

class PasswordInvalid(Unauthorized):
    def __init__(self, prop_name, prop):
        payload = {}
        payload[prop_name] = prop
        Unauthorized.__init__(
            self,
            'Invalid password for user with ' + prop_name + ' \'' + prop + '\'',
            payload
        )

class RoleInvalid(Unauthorized):
    def __init__(self, role):
        Unauthorized.__init__(self, 'User must have role \'' + role + '\'', {
            'role': role
        })

class ProviderInvalid(BadRequest):
    def __init__(self, provider):
        BadRequest.__init__(self, 'Provider \'' + provider + '\' is invalid', {
            'provider': provider
        })
