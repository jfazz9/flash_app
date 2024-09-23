from typing import Any
from django.core.management.base import BaseCommand
from cards.models import Topic

class Command(BaseCommand):
    help = 'Delete all topics from the database'

    def handle(self, *args, **kwargs):
        Topic.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all topics'))

        