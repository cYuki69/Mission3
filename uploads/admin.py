from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from .models import ImageSubmission, Mission

@admin.register(ImageSubmission)
class ImageSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'status', 'created_at', 'image_thumbnail')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'image_preview')

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" /></a>', obj.image.url)
        return "-"
    image_thumbnail.short_description = 'Thumbnail'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<a href="{0}" target="_blank"><img src="{0}" style="max-width: 400px; max-height: 400px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);" /></a>', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    fieldsets = (
        ('Submitter Info', {
            'fields': ('name', 'email', 'message', 'created_at')
        }),
        ('Submission Details', {
            'fields': ('image', 'image_preview', 'status')
        }),
    )

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'assignee_email', 'deadline', 'status', 'created_at')
    list_filter = ('status', 'deadline')
    search_fields = ('title', 'assignee_email', 'description')
    readonly_fields = ('id', 'created_at', 'completion_notes', 'completion_file')
    fieldsets = (
        ('Mission Details', {
            'fields': ('title', 'description', 'assignee_email', 'deadline', 'status', 'related_submission')
        }),
        ('Completion Details', {
            'fields': ('completion_notes', 'completion_file')
        }),
        ('Meta', {
            'fields': ('id', 'created_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        is_new = not change
        super().save_model(request, obj, form, change)
        
        if is_new and obj.assignee_email:
            secure_link = f"http://127.0.0.1:8000/mission/{obj.id}/"
            subject = f"New Mission Assigned: {obj.title}"
            message = f"You have been assigned a new mission.\n\nTitle: {obj.title}\nDescription: {obj.description}\nDeadline: {obj.deadline.strftime('%Y-%m-%d %H:%M %Z')}\n\nPlease access your secure portal to submit your work:\n{secure_link}"
            from_email = getattr(settings, 'EMAIL_HOST_USER', 'noreply@example.com') or 'noreply@example.com'
            
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [obj.assignee_email],
                    fail_silently=True,
                )
            except Exception as e:
                pass
