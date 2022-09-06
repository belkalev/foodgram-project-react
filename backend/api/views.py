from http import HTTPStatus

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, IngredientAmount, Ingredient, Recipes,
                            Shoplist, Tags)
from users.models import Follow, User

from .filters import IngredientsFilter, RecipesFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrAuthor, IsAdminOrReadOnly
from .serializers import (FollowSerializer, IngredientsSerializer,
                          ListUserSerializer, RecipeForFollowersSerializer,
                          RecipesCreateSerializer, RecipesSerializer,
                          TagsSerializer)

SUBSCRIBE_TO_YOURSELF = 'Нельзя подписаться на самого себя'
NO_SUBSCRIPTION = 'Нельзя отписаться от автора, на которго вы не подписаны'
DELETE_RECIPE = 'Рецепт удален'


class UsersViewSet(UserViewSet):
    """
    Вьюсет модели пользователей.
    """
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny,)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user.id == author.id:
                raise ValidationError(SUBSCRIBE_TO_YOURSELF)
            else:
                serializer = FollowSerializer(
                    Follow.objects.create(user=request.user, author=author),
                    context={'request': request},
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if Follow.objects.filter(
                    user=request.user, author=author).exists():
                Follow.objects.filter(
                    user=request.user, author=author
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': NO_SUBSCRIPTION},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    pagination_class = None
    serializer_class = TagsSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientsSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientsFilter


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    permission_classes = (IsAdminOrAuthor,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        return RecipesSerializer if self.action in (
            'list', 'retrieve'
        ) else RecipesCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        if model.objects.filter(
                recipe=recipe,
                user=request.user,
        ).exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        model.objects.create(recipe=recipe, user=request.user)
        serializer = RecipeForFollowersSerializer(recipe)
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    def delete_recipe(self, model, request, pk):
        recipe = get_object_or_404(Recipes, id=pk)
        if model.objects.filter(
                user=request.user,
                recipe=recipe,
        ).exists():
            model.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        return self.add_recipe(
            Favorite, request, pk
        ) if request.method == 'POST' else self.delete_recipe(
            Favorite, request, pk
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.add_recipe(
            Shoplist, request, pk
        ) if request.method == 'POST' else self.delete_recipe(
            Shoplist, request, pk
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        file_name = 'shopping_list.txt'
        if not user.shopping_cart.exists():
            return Response(status=HTTPStatus.BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit',
        ).annotate(
            value=Sum('amount')
        ).order_by('ingredients__name')
        response = HttpResponse(
            content_type='text/plain',
            charset='utf-8',
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        response.write('Список продуктов к покупке:\n')
        for ingredient in ingredients:
            response.write(
                f'- {ingredient["ingredients__name"]} '
                f'- {ingredient["value"]} '
                f'{ingredient["ingredients__measurement_unit"]}\n'
            )
        return response
