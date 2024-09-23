from django.contrib import admin
from .models import Topic

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)  # This will display the topic name in the admin list view
    search_fields = ('name',)  # Adds a search bar to easily find topics
