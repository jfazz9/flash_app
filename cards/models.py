# cards/models.py
from django.db import models
from django.contrib.auth.models import User

NUM_BOXES = 5
BOXES = range(1, NUM_BOXES + 1)

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Card(models.Model):
    question = models.CharField(max_length=500)
    answer = models.CharField(max_length=1000)
    box = models.IntegerField(
        choices=zip(BOXES, BOXES),
        default=BOXES[0],
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.question
    
    def move(self, solved):
        new_box = self.box + 1 if solved else BOXES[0]
        if new_box in BOXES:
            self.box = new_box
            self.save()
        return self

class Flashcard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=500)
    answer = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

