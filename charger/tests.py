from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
import os
import tempfile
from django.conf import settings
from django.db import IntegrityError

from .models import Task

# Use a temporary directory for test media files
TEST_MEDIA_ROOT = tempfile.mkdtemp()

# Override media root for tests
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT, MEDIA_URL='/media/')
class TaskModelTest(TestCase):

    def setUp(self):
        # Create a sample task for testing
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            completed=False
        )
        
        # Create a sample file for testing file uploads
        self.test_file = SimpleUploadedFile(
            'test_file.txt',
            b'This is a test file',
            content_type='text/plain'
        )
    
    def test_task_creation(self):
        """Test that a task is created with the correct attributes"""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'This is a test task')
        self.assertFalse(self.task.completed)
        # FileField is never None, it's a FieldFile object that may be empty
        self.assertFalse(bool(self.task.attached_file))
    
    def test_task_string_representation(self):
        """Test the string representation of the task"""
        self.assertEqual(str(self.task), 'Test Task')
    
    def test_required_fields(self):
        """Test that required fields are enforced"""
        # Test missing title (required field)
        task = Task(description='Missing title', completed=False)
        with self.assertRaises(ValidationError):
            task.full_clean()
            task.save()
            
        # Test missing description (required field)
        task = Task(title='Missing Description', completed=False)
        with self.assertRaises(ValidationError):
            task.full_clean()
            task.save()
            
        # Test valid task creation
        try:
            task = Task(title='Valid Task', description='Valid description', completed=False)
            task.full_clean()  # This should not raise an exception
            task.save()
        except ValidationError:
            self.fail("Valid task creation raised ValidationError unexpectedly")
    
    def test_optional_fields(self):
        """Test that optional fields work as expected"""
        # Close any existing file handles
        if hasattr(self, 'test_file'):
            if hasattr(self.test_file, 'close'):
                self.test_file.close()
        
        # Create a new file for this test
        test_file = SimpleUploadedFile(
            'test_optional.txt',
            b'Test optional file',
            content_type='text/plain'
        )
        
        task_with_file = Task.objects.create(
            title='Task with file',
            description='Has an attached file',
            completed=True,
            attached_file=test_file
        )
        self.assertTrue(task_with_file.completed)
        self.assertIsNotNone(task_with_file.attached_file)
        
        # Close the file handle and clean up
        if task_with_file.attached_file:
            if hasattr(task_with_file.attached_file, 'close'):
                task_with_file.attached_file.close()
            if os.path.exists(task_with_file.attached_file.path):
                try:
                    os.remove(task_with_file.attached_file.path)
                except PermissionError:
                    pass
    
    def test_task_ordering(self):
        """Test task ordering (by default, by id)"""
        task2 = Task.objects.create(
            title='Second Task',
            description='This is another test task'
        )
        tasks = list(Task.objects.all())
        self.assertEqual(tasks[0].title, 'Test Task')
        self.assertEqual(tasks[1].title, 'Second Task')
    
    def test_file_upload(self):
        """Test file upload functionality"""
        # Close any existing file handles
        if hasattr(self, 'test_file'):
            if hasattr(self.test_file, 'close'):
                self.test_file.close()
        
        # Create a new file for this test
        test_file = SimpleUploadedFile(
            'test_upload.txt',
            b'Test file content',
            content_type='text/plain'
        )
        
        task = Task.objects.create(
            title='File Upload Test',
            description='Testing file upload',
            attached_file=test_file
        )
        
        # Verify file exists
        self.assertTrue(os.path.exists(task.attached_file.path))
        
        # Close the file handle
        task.attached_file.close()
        
        # Clean up
        if os.path.exists(task.attached_file.path):
            os.remove(task.attached_file.path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run"""
        # Remove the temporary media directory and all its contents
        import shutil
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()
