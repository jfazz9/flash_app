from django.core.management.base import BaseCommand
from cards.models import Topic


class Command(BaseCommand):
    help = 'Add a new topic by taking input from the user'

    def handle(self, *args, **kwargs):
        # Ask the user for the topic name
        topic_name = input("Enter the new topic name: ")
        
        # Create or update the topic in the database
        topic, created = Topic.objects.get_or_create(name=topic_name)
        print(topic)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Successfully created new topic: {topic_name}"))
        else:
            self.stdout.write(self.style.WARNING(f"Topic '{topic_name}' already exists."))