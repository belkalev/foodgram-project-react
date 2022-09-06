from django.contrib import admin

from .models import (Favorite, IngredientAmount, Ingredient, Recipes,
                     Shoplist, Tags)


class RecipeIngredientsAdmin(admin.StackedInline):
    model = IngredientAmount
    autocomplete_fields = ('ingredients',)


@admin.register(Recipes)
class ResipesAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'text',)
    search_fields = ('text',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'color')
    empty_value_display = '-пусто-'


@admin.register(Shoplist)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
    empty_value_display = '-пусто-'
