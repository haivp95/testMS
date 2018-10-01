from django.db import models

# Create your models here.

class TestModel:
    def __init__(self, id, username, vote, datetime):
        self.id = id
        self.username = username
        self.vote = vote
        self.datetime = datetime
        
