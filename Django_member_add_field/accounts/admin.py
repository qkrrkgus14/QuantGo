from django.contrib import admin
from .models import Profile

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id","user","phone_number","address"]
    list_display_links = ["user"]
