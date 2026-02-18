"""drone_project URL Configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('drone.urls')),
    path('profile/', include('connector.urls')),
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
