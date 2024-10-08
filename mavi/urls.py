from django.urls import path


from django.conf import settings
from django.conf.urls.static import static

from . import views, utils

app_name = 'mavi'


urlpatterns = [
    # Rutas de app.
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('login_register/', views.login_register, name='login_register'),
    path("activate_account_view/", views.activate_account_view, name="activate_account"),
    path("register_done_viewes/", views.register_done_viewes, name="register_done"),
    path('password_reset/', views.password_reset_request_view, name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('password-reset-done/', views.password_reset_done_view, name='password_reset_done'),
    path('logout/', views.logout, name='logout'),
    path('plans/', views.plans, name='plans'),
    path("screen/", views.screen, name="screen"),
    path('upload_publicity/', views.upload_publicity, name='upload_publicity'),
    path('payment/', views.payment, name='payment'),
    
    
    # Rutas para funcionalidas.
    path('reupload_publicity/<str:publicity_id>', utils.reupload_publicity, name='reupload_publicity'),
    path('delete_publicity/<str:publicity_id>', utils.delete_publicity, name='delete_publicity')
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)