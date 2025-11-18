
from django.contrib import admin
from .models import Category, Application

admin.site.register(Category)
admin.site.register(Application)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-created_at',)
    # Чтобы изменять статус прямо в списке, можно использовать list_editable:
    # list_editable = ('status',)
