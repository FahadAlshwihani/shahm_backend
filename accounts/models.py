from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# -----------------------------
# Custom User Manager
# -----------------------------
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, role="viewer", **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            role=role,
            is_active=True,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Required internally by Django admin, not used externally."""
        extra_fields.setdefault("role", "super_admin")
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


# -----------------------------
# Custom User Model
# -----------------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("super_admin", "Super Admin"),
        ("admin", "Admin"),
        ("editor", "Editor"),
        ("viewer", "Viewer"),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")

    is_active = models.BooleanField(default=True)

    # 🔥 مهم جداً — عشان Django admin و middleware
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
