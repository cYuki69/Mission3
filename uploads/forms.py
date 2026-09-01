import os
import re
from datetime import datetime, time
from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import ImageSubmission, Mission

class ImageSubmissionForm(forms.ModelForm):
    class Meta:
        model = ImageSubmission
        fields = ['name', 'email', 'message', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email', 'required': 'required'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Optional Message'}),
            'image': forms.FileInput(attrs={'class': 'form-control d-none', 'id': 'imageInput', 'accept': '.jpg,.jpeg,.png,.webp'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # Basic sanitization
        if name:
            return name.strip()
        return name
        
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if message:
            return message.strip()
        return message

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image
        
        # Max size 10MB
        max_size = 10 * 1024 * 1024
        if image.size > max_size:
            raise ValidationError(_('Please keep filesize under %(size)s. Current filesize %(current)s') % {
                'size': filesizeformat(max_size),
                'current': filesizeformat(image.size)
            })

        # Check extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError(_('Unsupported file extension. Allowed extensions are: %s.') % ', '.join(valid_extensions))
        
        # Check MIME type
        valid_mime_types = ['image/jpeg', 'image/png', 'image/webp']
        if hasattr(image, 'content_type') and image.content_type not in valid_mime_types:
            raise ValidationError(_('Unsupported file type. Expected JPEG, PNG, or WebP.'))

        return image

class MissionSubmissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['completion_notes', 'completion_file']
        widgets = {
            'completion_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe how you completed the mission...'}),
            'completion_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class MissionCommandForm(forms.Form):
    command = forms.CharField(
        label='Mission command',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'เช่น ส่งรูปแมวก่อน 18:21',
            'required': 'required',
        }),
    )

    def clean_command(self):
        command = self.cleaned_data['command'].strip()
        match = re.search(r'ก่อน\s*(\d{1,2}):(\d{2})', command)
        if not match:
            raise ValidationError('ใช้รูปแบบคำสั่ง เช่น “ส่งรูปแมวก่อน 18:21”')

        hour, minute = (int(value) for value in match.groups())
        if hour > 23 or minute > 59:
            raise ValidationError('เวลาต้องอยู่ระหว่าง 00:00 ถึง 23:59')

        task = command[:match.start()].strip()
        if not task:
            raise ValidationError('ระบุสิ่งที่ต้องทำก่อนเวลา เช่น “ส่งรูปแมว”')

        deadline = timezone.make_aware(
            datetime.combine(timezone.localdate(), time(hour, minute)),
            timezone.get_current_timezone(),
        )
        self.cleaned_data['title'] = task
        self.cleaned_data['deadline'] = deadline
        return command
