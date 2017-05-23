from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, BooleanField
from django.db.models import F
from django.db.models import When
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from blogs.models import Blog, Post, Subscription


class BlogExist(object):

    def dispatch(self, request, *args, **kwargs):
        self.blog = get_object_or_404(Blog, slug=kwargs.get('slug'))
        return super(BlogExist, self).dispatch(request, *args, **kwargs)


class BlogsView(ListView):

    model = Blog
    template_name = 'blogs/blogs.html'
    context_object_name = 'blogs'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.is_authenticated:
            blogs_ids = Subscription.objects.filter(
                owner=self.request.user
            ).values_list('blog', flat=True)
            qs = self.model.objects.annotate(
                has_subscription=Case(
                    When(pk__in=blogs_ids, then=True),
                    default=False,
                    output_field=BooleanField(),
                ),
            )
        else:
            qs = self.model.objects.all()

        return qs


class BlogView(BlogExist, ListView):
    model = Post
    template_name = 'blogs/posts.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        ctx = super(BlogView, self).get_context_data(**kwargs)
        ctx['blog'] = self.blog

        return ctx

    def get_queryset(self):
        return self.model.objects.select_related('blog').filter(blog=self.blog)


class AddPostView(BlogExist, CreateView):
    model = Post
    template_name = 'blogs/post_update.html'
    fields = ['title', 'text']

    def get_success_url(self):
        return reverse('blogs:blog', kwargs={'slug': self.kwargs['slug']})

    def form_valid(self, form):
        form.instance.blog = self.blog
        return super(AddPostView, self).form_valid(form)


class PostView(BlogExist, DetailView):
    model = Post
    template_name = 'blogs/post.html'

    def get_context_data(self, **kwargs):
        ctx = super(PostView, self).get_context_data(**kwargs)
        ctx['subscription'] = self.object.subscription(self.request.user)
        ctx['is_readed'] = self.object.readed_by_user(
            self.request.user,
            subscription=ctx['subscription']
        )
        return ctx


class UpdatePostView(BlogExist, UpdateView):
    model = Post
    template_name = 'blogs/post_update.html'
    fields = ['title', 'text']

    def get_success_url(self):
        return reverse('blogs:blog', kwargs={'slug': self.kwargs['slug']})


class AddSubscriptionView(BlogExist, CreateView):
    model = Subscription
    fields = ['blog', 'owner']
    template_name = 'index.html'
    success_url = reverse_lazy('blogs:blogs')

    def get_form_kwargs(self):
        kwargs = super(AddSubscriptionView, self).get_form_kwargs()
        if self.request.method == 'POST':
            data = dict(kwargs['data'])
            data.update({
                'blog': self.blog.pk,
                'owner': self.request.user.pk,
            })
            kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        form.instance.blog = self.blog
        return super(AddSubscriptionView, self).form_valid(form)


class DeleteSubscriptionView(BlogExist, DeleteView):
    model = Subscription
    success_url = reverse_lazy('blogs:blogs')

    def get_object(self, queryset=None):
        qs = queryset or self.get_queryset()
        obj = qs.filter(
            owner=self.request.user,
            blog=self.blog
        ).first()

        if obj is None:
            raise Http404('Блог не найден')

        return obj


class FeedView(LoginRequiredMixin, ListView):

    model = Post
    template_name = 'blogs/feed.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        readed_ids = self.model.objects.filter(
            blog__subscriptions__owner__in=[self.request.user]
        ).values_list('blog__subscriptions__readed', flat=True).distinct()

        qs = self.model.objects.filter(
            blog__subscriptions__owner__in=[self.request.user]
        ).annotate(
            readed=Case(
                When(pk__in=readed_ids, then=True),
                default=False,
                output_field=BooleanField(),
            ),
        ).order_by('-created_at')

        return qs


class AddReadedView(View):

    def dispatch(self, request, *args, **kwargs):
        # выбираем так, чтобы сэкономить 1 запрос
        self.blog_post = Post.objects.select_related('blog').filter(pk=kwargs.get('pk')).first()

        if self.post is None:
            raise Http404

        self.subscription = get_object_or_404(
            Subscription,
            blog=self.blog_post.blog,
            owner=self.request.user
        )
        return super(AddReadedView, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        # форма будет без инпутов и используется только чтобы отправить запрос методом post
        # и если до этого момента не получили 404, то все валидно и можем добавлять пост в прочитанные
        self.subscription.readed.add(self.blog_post)
        return redirect('blogs:feed')



