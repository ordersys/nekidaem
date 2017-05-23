from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from app.views import index

urlpatterns = [
    url(r'^$', index,  name='index'),
    url(r'^blogs/', include('blogs.urls')),
    url(r'^admin/', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
