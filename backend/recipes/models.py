from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        'Ингредиент',
        max_length=200,
        blank=False,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200,
    )

    class Meta:
        ordering = ['id', ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Тэги'
    )
    color = models. CharField(
        max_length=20,
        unique=True,
        verbose_name='Цвет'
    )
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт',
        null=True
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientAmount",
        related_name="recipes",
        verbose_name="Ингридиент",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="recipes",
        verbose_name="Тэги",
    )
    cooking_time = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(
                0, "Время приготовления не может быть отрицательным"
            ),
            MaxValueValidator(
                43260, "Точно так долго?"
            ),
        ],
        verbose_name="Время приготовления",
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.name[:15]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorute',
        verbose_name='Избранные рецепты'
    )
    added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_fav',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} добавлен в избранные пользователем {self.user}'


class Shoplist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shop',
        verbose_name='Рецепты'
    )
    added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_list',
            ),
        ]


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ing_amounts",
        verbose_name="Рецепт",
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ing_amounts",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0, "Количество не может быть отрицательным"),
            MaxValueValidator(10000, "А куда вам столько?"),
        ],
        verbose_name="Количество",
    )

    class Meta:
        verbose_name = 'Ингридиент'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredients', 'recipe',),
                name='ing_recipe'
            )
        ]
