from django.urls import path
from users.views import tenant_view, LoginView, RegisterView, LogoutView, EmailRedirectView

urlpatterns = [
    path("", EmailRedirectView.as_view(), name="home_redirect"),  # Redirect root to login
    path("<tenant_name>/", tenant_view, name="tenant_home"),  # Dynamic URL cho từng tenant
    path("login/", EmailRedirectView.as_view(), name="email_redirect"),
    path("login1/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
