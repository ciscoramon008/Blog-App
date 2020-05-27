class User:
    def __init__(self, username, email, image):
        self.username = username
        self.image = image
        self.email = email

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username
    
    def __eq__(self, other):
        return self.username == other.username and self.email == other.email and self.image == other.image