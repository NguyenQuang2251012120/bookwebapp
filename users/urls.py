from django.urls import path

from .views import LoginView, LogoutView, RegisterView, EmailRedirectView

urlpatterns = [
    path("login/", EmailRedirectView.as_view(), name="email_redirect"),  # Trang nhập email
    path("login1/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
