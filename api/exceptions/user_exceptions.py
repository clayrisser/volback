from nails.exceptions import NotFound

class UserNotFound(NotFound):
    message = 'User not found'

    def __init__(self, email):
        NotFound.__init__(self, 'User with email \'' + email + '\' already exists', {
            'email': email
        });
