from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('', include('invoice.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
]

handler500 = 'invoice.views.error_500'
handler404 = 'invoice.views.error_404'
