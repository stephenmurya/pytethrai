from django.contrib import admin
from .models import Tag, LibraryItem

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')

@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'user', 'created_at')
    list_filter = ('item_type', 'user')
    search_fields = ('title', 'content')
