from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .manager import UserManager


class CustomUser(AbstractUser):
    username = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Profile(models.Model):
    class Roles(models.TextChoices):
        MANAGER = "MA", _("Manager")
        QA = "QA", _("QA")
        DEVELOPER = "DEV", _("Developer")

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=256, choices=Roles.choices, default=Roles.DEVELOPER
    )
    contact_number = models.CharField(max_length=12)

    def __str__(self):
        return str(self.user)


class Project(models.Model):
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    team_members = models.ManyToManyField(Profile, related_name="projects")

    def __str__(self):
        return self.title


class Task(models.Model):
    class Status(models.TextChoices):
        OPEN = "OP", _("Open")
        REVIEW = "REV", _("Review")
        WORKING = "WOR", _("Working")
        AWAITING_RELEASE = "AWAIT", _("Awaiting Release")
        WAITING_QA = "WAIT", _("Waiting QA")

    title = models.CharField(max_length=256)
    description = models.CharField(max_length=512)
    status = models.CharField(
        max_length=256, choices=Status.choices, default=Status.OPEN
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="tasks"
    )
    assignee = models.ManyToManyField(Profile, related_name="tasks")

    def __str__(self):
        return self.title


class Document(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=512)
    file = models.FileField(upload_to="uploads")
    version = models.CharField(max_length=256)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, related_name="documents"
    )

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.CharField(max_length=512)
    author = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="comments", null=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments", null=True
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="comments", null=True
    )

    def __str__(self):
        return self.text
