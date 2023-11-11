from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls import handler404, handler500

urlpatterns = [
    path('', include('invoice.urls')),
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='invoice/admin/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        template_name='invoice/admin/logout.html'), name='logout'),
]

handler500 = 'invoice.views.error_500'
handler404 = 'invoice.views.error_404'
