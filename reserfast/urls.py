
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reserfast/admin/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('reserfast/', include('reserfast_app.urls', namespace='reserfast')),
    path('password_reset/', include('django.contrib.auth.urls')),
    path('', RedirectView.as_view(url='/reserfast/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
