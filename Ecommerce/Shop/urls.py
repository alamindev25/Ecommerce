
from django.urls import path
from Shop import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .forms import LoginForm,MyPasswordChangeForm,MyPasswordReset,MySetPasswordForm

urlpatterns = [
    path('', views.ProductView.as_view(), name="home"),
    path('product-detail/<int:pk>',views.ProductDetail.as_view(),name="product-detail"),
    path('lehenga/', views.lehenga, name='lehenga'),
    path('lehenga/<slug:data>',views.lehenga, name='lehengaitem'),
    path('profile/',views.profile, name='profile'),
    path('registration/',views.CustomerRegistrationView.as_view(),name='customerregistration'),
    path('accounts/login/',auth_views.LoginView.as_view(template_name='Shop/login.html',authentication_form=LoginForm),name='login'),
    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name ='Shop/passwordchange.html', form_class= MyPasswordChangeForm, success_url='/passwordchangedone/'), name="passwordchange"),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('passwordchangedone/', auth_views.PasswordChangeView.as_view(template_name='Shop/passwordchangedone.html'), name="passwordchangedone"),

    path('password_reset',auth_views.PasswordResetView.as_view(template_name='Shop/password_reset.html', form_class=MyPasswordReset),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='Shop/password_reset_done.html'),name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='Shop/password_reset_confirm.html', form_class=MySetPasswordForm),name='password_reset_confirm'),
    path('password_reset_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='Shop/password_reset_complete.html'),name='password_reset_complete'),
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)