class User:
    def __init__(self, username: str, password_hash: str, role="user"):
        self.__username = username
        self.__password_hash = password_hash  
        self.__role = role
    
    def get_username(self) -> str:
        return self.__username
    
    def get_role(self) -> str:
        return self.__role


    def verify_password(self, input_password, bcrypt_wrapper):
        """Public method to verify password safely."""
        return bcrypt_wrapper.checkpw(input_password.encode(), self.__password_hash.encode())

    def __str__(self):
        return f"User(username='{self.__username}', role='{self.__role}')"