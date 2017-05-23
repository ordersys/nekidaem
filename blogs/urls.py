from django.conf.urls import url

from . import views

app_name = 'blogs'
urlpatterns = [
    url(
        r'^$',
        views.BlogsView.as_view(),
        name='blogs'
    ),
    url(
        r'^feed/$',
        views.FeedView.as_view(),
        name='feed'
    ),
    url(
        r'^(?P<pk>\d+)/add_to_readed/$',
        views.AddReadedView.as_view(),
        name='add_to_readed'
    ),
    url(
        r'^(?P<slug>[-\w]+)/$',
        views.BlogView.as_view(),
        name='blog'
    ),
    url(
        r'^(?P<slug>[-\w]+)/add/$',
        views.AddPostView.as_view(),
        name='add_post'
    ),
    url(
        r'^(?P<slug>[-\w]+)/add_subscription/$',
        views.AddSubscriptionView.as_view(),
        name='add_subscription'
    ),
    url(
        r'^(?P<slug>[-\w]+)/delete_subscription/$',
        views.DeleteSubscriptionView.as_view(),
        name='delete_subscription'
    ),
    url(
        r'^(?P<slug>[-\w]+)/(?P<pk>\d+)/$',
        views.PostView.as_view(),
        name='post'
    ),
    url(
        r'^(?P<slug>[-\w]+)/(?P<pk>\d+)/update/$',
        views.UpdatePostView.as_view(),
        name='update_post'
    ),
]