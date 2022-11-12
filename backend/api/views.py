from http import HTTPStatus

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe,
                            Shoplist, Tag)

from users.models import Follow, User
from .service import get_ingredients_for_shopping
from .filters import IngredientsFilter, RecipesFilter
from .pagination import LimitPageNumberPagination
from .permissions import IsAdminOrAuthor, IsAdminOrReadOnly
from .serializers import (FollowSerializer, IngredientsSerializer,
                          ListUserSerializer, RecipeForFollowersSerializer,
                          RecipesCreateSerializer, RecipesSerializer,
                          TagsSerializer)


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
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
            serializer = FollowSerializer(
                Follow.objects.create(user=request.user, author=author),
                context={'request': request},
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        Follow.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagsSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientsFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrAuthor,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesSerializer
        return RecipesCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def __add_recipe(model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(recipe=recipe, user=request.user)
        serializer = RecipeForFollowersSerializer(recipe)
        return Response(data=serializer.data, status=HTTPStatus.CREATED)

    @staticmethod
    def __delete_recipe(model, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.filter(recipe=recipe, user=request.user).delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.__add_recipe(Favorite, request, pk)
        return self.__delete_recipe(Favorite, request, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def recipe(self, request, pk):
        if request.method == 'POST':
            return self.__add_recipe(Recipe, request, pk)
        return self.__delete_recipe(Recipe, request, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.__add_recipe(Shoplist, request, pk)
        return self.__delete_recipe(Shoplist, request, pk)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        return get_ingredients_for_shopping(user)
