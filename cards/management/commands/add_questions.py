from django.core.management.base import BaseCommand
from cards.models import Card, Topic
import os
import re

class Command(BaseCommand):
    help = 'Import questions and answers from a text file into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the .txt file containing questions and answers')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} does not exist"))
            return


        with open(file_path, 'r') as file:
            text = file.read()

        pattern = r'(\d+\.\s.*?\?)\s*(-\s.*?)(?=\d+\.|$)'
        matches = re.findall(pattern, text, re.DOTALL)

        if not matches:
            self.stdout.write(self.style.ERROR("No valid question-answer pairs found in the file."))
            return
        
        topic_name = input("Enter the new topic name: ")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully created new topic: {topic_name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Topic '{topic_name}' already exists."))

        for question, answer in matches:
            Card.objects.create(question=question.strip(), answer=answer.strip(), box=1, topic=topic)
            self.stdout.write(self.style.SUCCESS(f"Added: {question} - {answer}"))

        
            

        #Create or update the topic in the database




