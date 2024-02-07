from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text=('Снимите галочку, '
                   'чтобы скрыть публикацию.')
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )

    description = models.TextField(
        verbose_name='Описание'
    )

    slug = models.SlugField(
        unique=True,
        blank=False,
        null=False,
        verbose_name='Идентификатор',
        help_text=('Идентификатор страницы для URL; '
                   'разрешены символы латиницы, цифры, '
                   'дефис и подчёркивание.')
    )

    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места'
    )

    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(BaseModel):
    title = models.CharField(
        max_length=256,
        verbose_name='Заголовок'
    )

    text = models.TextField(
        verbose_name='Текст'
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=('Если установить дату и время '
                   'в будущем — можно делать '
                   'отложенные публикации.')
    )

    image = models.ImageField(
        'Фото',
        blank=True,
        upload_to='post_images'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        blank=False
    )

    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение'
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )

    created_at = models.DateTimeField(
        verbose_name='Добавлено',
        auto_now_add=True
    )

    def comment_count(self):
        return Comments.objects.filter(post=self).count()

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={"pk": self.pk})

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']
        default_related_name = 'posts'

    def __str__(self):
        return self.title


class Comments(models.Model):
    text = models.TextField(
        'Текст коментария'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        blank=False
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('created_at',)
