from nails.exceptions import NotFound, Forbidden

class UserNotFound(NotFound):
    def __init__(self, field_name, field_data):
        self.message = 'User with ' + field_name + ' \'' + field_data + '\' not found'
        payload = {}
        payload[field_name] = field_data
        NotFound.__init__(
            self,
            self.message,
            payload
        )

class UserWithPropExists(Forbidden):
    def __init__(self, prop_name, prop):
        self.message = 'User with ' + prop_name + ' \'' + prop + '\' already exists'
        payload = {}
        payload[prop_name] = prop
        Forbidden.__init__(
            self,
            self.message,
            payload
        )
