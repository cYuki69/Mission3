import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import ImageSubmissionForm
from .models import ImageSubmission

class ImageSubmissionFormTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test message',
        }

    def test_valid_image_upload(self):
        import tempfile
        from PIL import Image
        image = Image.new('RGB', (100, 100), color = 'red')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file, format='PNG')
        tmp_file.seek(0)
        img_content = tmp_file.read()
        img_file = SimpleUploadedFile(
            name='test.png',
            content=img_content,
            content_type='image/png'
        )
        
        form = ImageSubmissionForm(data=self.valid_data, files={'image': img_file})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_extension(self):
        # Create a file with a .txt extension
        img_file = SimpleUploadedFile(
            name='test.txt',
            content=b'Not an image',
            content_type='text/plain'
        )
        
        form = ImageSubmissionForm(data=self.valid_data, files={'image': img_file})
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
        self.assertTrue(len(form.errors['image']) > 0)

    def test_file_too_large(self):
        # Create a file larger than 10MB
        large_content = b'0' * (10 * 1024 * 1024 + 1)
        img_file = SimpleUploadedFile(
            name='large.jpg',
            content=large_content,
            content_type='image/jpeg'
        )
        
        form = ImageSubmissionForm(data=self.valid_data, files={'image': img_file})
        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
        self.assertTrue(len(form.errors['image']) > 0)

from django.core import mail
from django.utils import timezone
from datetime import timedelta
from .models import Mission
from .admin import MissionAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

class MissionAdminTest(TestCase):
    def test_mission_assignment_sends_email(self):
        site = AdminSite()
        admin_class = MissionAdmin(Mission, site)
        
        mission = Mission(
            title="Review Image 1",
            description="Please review this uploaded image.",
            assignee_email="reviewer@example.com",
            deadline=timezone.now() + timedelta(days=2),
        )
        
        # Simulate saving a new model via the admin interface
        admin_class.save_model(None, mission, None, False)
        
        # Verify that an email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "New Mission Assigned: Review Image 1")
        self.assertIn("Please access your secure portal to submit your work:", mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ["reviewer@example.com"])


class MissionCommandTest(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='admin', password='test-password', is_staff=True,
        )

    def test_command_creates_a_mission_with_a_deadline(self):
        self.client.force_login(self.admin)
        response = self.client.post('/mission/create/', {
            'command': 'ส่งรูปแมวก่อน 18:21',
        })

        self.assertEqual(response.status_code, 302)
        mission = Mission.objects.get()
        self.assertEqual(mission.title, 'ส่งรูปแมว')
        self.assertEqual(mission.description, 'ส่งรูปแมวก่อน 18:21')
        local_deadline = timezone.localtime(mission.deadline)
        self.assertEqual(local_deadline.hour, 18)
        self.assertEqual(local_deadline.minute, 21)

    def test_command_requires_a_time(self):
        self.client.force_login(self.admin)
        response = self.client.post('/mission/create/', {
            'command': 'ส่งรูปแมว',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ใช้รูปแบบคำสั่ง')

    def test_mission_management_requires_an_admin_login(self):
        response = self.client.get('/missions/')

        self.assertRedirects(response, '/admin/login/?next=/missions/')
