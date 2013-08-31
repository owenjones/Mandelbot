# Mandelbot
"""
UserList
"""

class UserList(list) :
    users = []

    def add(self, user) :
        self.users.append(user)

    def remove(self, nickname) :
        
