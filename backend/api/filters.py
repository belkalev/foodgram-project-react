from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientsFilter(filters.FilterSet):
    """
    Фильтр ингредиентов.
    """
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(filters.FilterSet):
    """
    Фильтр рецептов.
    """
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='favorite_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='shopping_cart_filter'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def favorite_filter(self, queryset, name, value):
        return Recipe.objects.filter(favorite__user=self.request.user)

    def shopping_cart_filter(self, queryset, name, value):
        return Recipe.objects.filter(shopping_cart__user=self.request.user)

    class Meta:
        model = Recipe
        fields = ['author']
