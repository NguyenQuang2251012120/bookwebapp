import logging

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.generic import View
from .forms import LoginForm, RegisterForm
from users.models import Tenant, Domain
from django_tenants.utils import schema_context
from django.utils.text import slugify
from .forms import EmailForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse



def tenant_view(request, tenant_name):
    """
    Xử lý request dynamic cho từng tenant dựa trên tenant_name.
    """
    # Kiểm tra schema tương ứng với tenant_name
    tenant = get_object_or_404(Tenant, schema_name=tenant_name)

    # Sử dụng schema_context để chuyển đổi schema trong database
    with schema_context(tenant_name):
        # Ví dụ: Render trang Home riêng cho mỗi tenant
        return render(request, "tenant/home.html", {"tenant_name": tenant_name})



def create_tenant_for_user(user):
    schema_name = slugify(user.email.split('@')[0])  # Lấy phần trước dấu '@'

    # Kiểm tra trùng tên schema
    if Tenant.objects.filter(schema_name=schema_name).exists():
        logger.error(f"Schema name already exists for {schema_name}.")
        raise ValueError("Schema name already exists!")

    try:
        tenant = Tenant(
            schema_name=schema_name,
            name=f"{user.first_name}'s Library",
            owner=user,
        )
        tenant.save()
        logger.info(f"Tenant {schema_name} created successfully.")
    except Exception as e:
        logger.error(f"Failed to create tenant {schema_name}: {str(e)}")
        raise ValueError("Failed to create tenant.")

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

                # Chuyển hướng đến path của tenant dựa trên schema
                schema_name = slugify(email.split('@')[0])  # Lấy schema từ email
                return redirect(f"/{schema_name}/")  # URL dạng path routing
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

            # Tạo tenant mới
            create_tenant_for_user(user)
            logger.info(f"User {user.email} registered and tenant schema created.")

            # Chuyển hướng đến trang của tenant
            schema_name = slugify(user.email.split('@')[0])
            return redirect(f"/{schema_name}/")  # Chuyển đến Home của tenant
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
            schema_name = slugify(email.split('@')[0])  # Lấy schema từ email
            try:
                # Chuyển hướng dựa trên path routing
                return redirect(f"/{schema_name}/login1/?email={email}")
            except Tenant.DoesNotExist:
                form.add_error(None, "No tenant found for this email.")
                return render(request, "users/login.html", {"form": form})

        return render(request, "users/login.html", {"form": form})

