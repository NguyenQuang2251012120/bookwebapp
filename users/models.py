import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django_tenants.models import TenantMixin, DomainMixin
from django.db import models


class AbstractBaseModel(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.id:
            table_name = self.__class__.__name__.lower()
            self.id = f"{table_name}-{str(uuid.uuid4())}"
        super().save(*args, **kwargs)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        return self.create_user(email, password, **extra_fields)

class Tenant(TenantMixin):
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        "users.Librarian",
        on_delete=models.SET_NULL,  # Cho phép xóa liên kết khi người dùng bị xóa
        null=True,  # Cho phép giá trị null
        blank=True  # Cho phép giá trị rỗng
    )

    def __str__(self):
        return self.name

class Domain(DomainMixin):
    pass

class Librarian(AbstractUser, AbstractBaseModel):
    schema_name = models.CharField(max_length=100, null=True, blank=True)  # Schema của tenant
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    database_name = models.CharField(max_length=255, null=True, blank=True)  # Thêm trường này

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

