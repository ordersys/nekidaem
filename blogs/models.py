from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from app.utils import get_absolute_uri


class Blog(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('пользователь'),
        on_delete=models.CASCADE,
        related_name='blog'
    )
    name = models.CharField(_('название'), max_length=64, unique=True)
    slug = models.SlugField(
        _('страница блога'),
        max_length=64,
        null=True,
        editable=False,
        allow_unicode=True
    )

    class Meta:
        verbose_name = _('блог')
        verbose_name_plural = _('блоги')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, True)
        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    blog = models.ForeignKey(
        Blog,
        verbose_name=_('блог'),
        related_name='posts',
        on_delete=models.CASCADE
    )
    title = models.CharField(
        _('заголовок'),
        max_length=128,
    )
    text = models.TextField(
        _('текст'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        _('создан'),
        auto_now_add=True
    )

    @property
    def subscriptions(self):
        return Subscription.objects.filter(blog=self.blog)

    def subscription(self, user):
        if user.is_authenticated:
            return self.subscriptions.filter(owner=user).first()

    @property
    def subscribed_user_emails(self):
        return self.subscriptions.values_list('owner__email', flat=True)

    def readed_by_user(self, user, subscription=None):
        if subscription is None:
            subscription = self.subscription(user)

        if subscription is None:
            return False

        return self in subscription.readed.all()

    class Meta:
        verbose_name = _('пост')
        verbose_name_plural = _('посты')

    def get_absolute_url(self):
        return reverse('blogs:post', kwargs={'slug': self.blog.slug, 'pk': self.pk})

    def save(self, force_insert=False, force_update=False,
             using=None, update_fields=None):

        first_publish = False
        if self.pk is None:
            first_publish = True

        super(Post, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

        if first_publish:
            send_mail(
                'Новый пост.',
                'Новый пост %s' % get_absolute_uri(self.get_absolute_url()),
                settings.DEFAULT_FROM_EMAIL,
                self.subscribed_user_emails,
                fail_silently=False,
            )

    def delete(self, using=None, keep_parents=False):

        # TODO: про уведомления при удалении ничего не сказано, но если надо отправлять
        # TODO: то вызвать метод/ф-ию можно тут

        super(Post, self).delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return self.title


class Subscription(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('подписанный пользователь'),
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    blog = models.ForeignKey(
        Blog,
        verbose_name=_('блог'),
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    readed = models.ManyToManyField(
        Post,
        verbose_name=_('прочитанные посты'),
        related_name='+'
    )

    class Meta:
        verbose_name = _('подписка')
        verbose_name_plural = _('подписки')
        unique_together = ('owner', 'blog')

    def __str__(self):
        return '%s | %s' % (self.owner, self.blog)
