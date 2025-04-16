import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic import View
from .forms import LoginForm, RegisterForm
from users.models import Tenant, Domain
from django_tenants.utils import schema_context
from django.utils.text import slugify
from .forms import EmailForm


def create_tenant_for_user(user):
    # Chuyển đổi email thành định dạng slug để làm schema_name
    schema_name = slugify(user.email.split('@')[0])  # Lấy phần trước dấu '@' của email

    tenant = Tenant(
        schema_name=schema_name,
        name=f"{user.first_name}'s Library",
        owner=user,
    )
    tenant.save()

    domain = Domain(
        domain=f"{schema_name}.localhost",
        tenant=tenant,
    )
    domain.save()

logger = logging.getLogger(__name__)


class LoginView(View):
    """
    Login view
    get(): Returns the login page with the login form pre-filled with email
    post(): Authenticates the user and logs them in
    """
    def get(self, request, *args, **kwargs):
        # Lấy email từ session (nếu có) hoặc từ query parameter
        email = request.session.pop("last_email", "") or request.GET.get("email", "")
        form = LoginForm(initial={"email": email})  # Tiền điền email vào form

        # Làm email chỉ đọc
        form.fields["email"].widget.attrs["readonly"] = True

        return render(request, "users/login1.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)

                # Redirect to home page after login
                return redirect("/")
            form.add_error(None, "Invalid email or password")

        return render(request, "users/login1.html", {"form": form})




class RegisterView(View):
    """
    Register view
    get(): Returns the register page with the register form
    post(): Registers the user
    """

    def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")

            user.set_password(password)
            user.save()

            # Tạo schema cho người dùng mới đăng ký
            create_tenant_for_user(user)

            logger.info(f"User {user.email} registered and tenant schema created.")
            return redirect("login")
        logger.warning(f"Invalid registration attempt: {form.errors}")

        return render(request, "users/register.html", {"form": form})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        # Lưu email của người dùng vào session trước khi logout
        email = request.user.email if request.user.is_authenticated else ""
        request.session['last_email'] = email  # Lưu email vào session

        # Thực hiện logout
        logout(request)
        return redirect("login")  # Chuyển đến trang đăng nhập


class EmailRedirectView(View):
    """
    Handles redirect based on email provided.
    """
    def get(self, request, *args, **kwargs):
        form = EmailForm()
        return render(request, "users/login.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("email")
            schema_name = slugify(email.split('@')[0])  # Lấy phần đầu của email làm schema
            try:
                # Tìm domain dựa trên schema của tenant
                domain = Domain.objects.get(tenant__schema_name=schema_name)
                # Chuyển hướng đến login1 và đính kèm email
                return redirect(f"http://{domain.domain}:8000/login1/?email={email}")
            except Domain.DoesNotExist:
                form.add_error(None, "No tenant found for this email.")
                return render(request, "users/login.html", {"form": form})

        return render(request, "users/login.html", {"form": form})

