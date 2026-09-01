import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class ImageSubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PD', _('Pending')
        APPROVED = 'AP', _('Approved')
        REJECTED = 'RJ', _('Rejected')

    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField(blank=True)
    image = models.ImageField(upload_to='submissions/%Y/%m/%d/')
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Mission(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PD', _('Pending')
        COMPLETED = 'CP', _('Completed')
        OVERDUE = 'OD', _('Overdue')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignee_email = models.EmailField(blank=True)
    deadline = models.DateTimeField()
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PENDING,
    )
    related_submission = models.ForeignKey(
        ImageSubmission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='missions'
    )
    completion_notes = models.TextField(blank=True)
    completion_file = models.FileField(upload_to='mission_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
