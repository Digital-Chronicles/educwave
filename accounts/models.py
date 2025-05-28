from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    name = models.CharField(max_length=150, blank=True)  # Add this line

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        ACADEMIC = 'ACADEMIC', _('Academic')
        TEACHER = 'TEACHER', _('Teacher')
        FINANCE = 'FINANCE', _('Finance')
        STUDENT = 'STUDENT', _('Student')
        PARENT = 'PARENT', _('Parent')

    email = models.EmailField(_('email_address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = "custom_user"
        db_table_comment = "Custom user model using email for authentication with role-based access"

    def __str__(self):
        return f"{self.email} - {self.role}"
