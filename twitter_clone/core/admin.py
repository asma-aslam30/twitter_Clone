from django.contrib import admin
from .models import Profile, Tweet

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'birth_date')
    search_fields = ('user__username', 'location')

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at', 'total_likes')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')
