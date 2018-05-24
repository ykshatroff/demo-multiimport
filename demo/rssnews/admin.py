from demo.rssnews.models import Item, Author, Category
from django.contrib.admin import register, ModelAdmin


@register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = 'name',


@register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = 'title',


@register(Item)
class ItemAdmin(ModelAdmin):
    list_display = 'title', 'date_published'
