from app.models import Comment, CustomUser, Document, Profile, Project, Task
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class BaseAPITestCase(APITestCase):

    def setUp(self):
        self.login = "/api/token/"
        self.register = "/api/register/"
        self.user = CustomUser.objects.create(
            email="abdul4@gmail.com", username="abdul"
        )
        self.user.set_password("123456")
        self.user.save()

        self.profile = Profile.objects.create(
            user=self.user, role="MA", contact_number="123456789"
        )
        self.profile.save()

        self.user1 = CustomUser.objects.create(
            email="abdul5@gmail.com", username="abdul5"
        )
        self.user1.set_password("123456")
        self.user1.save()

        self.profile1 = Profile.objects.create(
            user=self.user1, role="DEV", contact_number="123456789"
        )
        self.profile1.save()

        self.project = Project.objects.create(
            title="test project",
            description="test description",
        )
        self.project.team_members.add(self.profile)
        self.project.save()

        self.project1 = Project.objects.create(
            title="test project 2",
            description="test description 2",
        )
        self.project1.team_members.add(self.profile1)
        self.project1.save()

        self.task = Task.objects.create(
            title="test task",
            description="test task description",
            status="OP",
            project=self.project,
        )
        self.task.save()

        self.document = Document.objects.create(
            name="test name",
            description="test doc description",
            project=self.project,
        )
        self.document.save()

        self.comment = Comment.objects.create(
            text="test comment",
            author=self.profile,
            task=self.task,
            project=self.project,
        )
        self.comment.save()
        self.client = APIClient()

        data = {"email": self.user.email, "password": "123456"}
        response = self.client.post(self.login, data, format="json")
        self.access = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

        self.client1 = APIClient()

        data = {"email": self.user1.email, "password": "123456"}
        response = self.client1.post(self.login, data, format="json")
        self.access1 = response.data["access"]
        self.client1.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access1}")


class TestLoginAPI(BaseAPITestCase):
    login = "/api/token/"

    def setUp(self):
        return super().setUp()

    def test_user_login(self):
        data = {"email": self.user.email, "password": "123456"}
        response = self.client.post(self.login, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_login_email_fail(self):
        data = {"email": "abdul@gmail.com", "password": "123456"}
        response = self.client.post(self.login, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_password_fail(self):
        data = {"email": self.user.email, "password": "12345"}
        response = self.client.post(self.login, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestRegisterAPI(BaseAPITestCase):
    login = "/api/register/"

    def setUp(self):
        return super().setUp()

    def test_register_user(self):
        data = {
            "user": {
                "username": "abdul3",
                "email": "abdul3@gmail.com",
                "password": "R@m@_f0rtu9e$",
            },
            "role": "DEV",
            "contact_number": "123456789",
        }
        response = self.client.post(self.register, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_email_fail(self):
        data = {
            "user": {
                "username": "abdul3",
                "email": "abdul4@gmail.com",
                "password": "R@m@_f0rtu9e$",
            },
            "role": "DEV",
            "contact_number": "123456789",
        }
        response = self.client.post(self.register, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_username_fail(self):
        data = {
            "user": {
                "username": "abdul",
                "email": "abdul3@gmail.com",
                "password": "R@m@_f0rtu9e$",
            },
            "role": "DEV",
            "contact_number": "123456789",
        }
        response = self.client.post(self.register, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_password_fail(self):
        data = {
            "user": {
                "username": "abdul3",
                "email": "abdul3@gmail.com",
                "password": "123456",
            },
            "role": "DEV",
            "contact_number": "123456789",
        }
        response = self.client.post(self.register, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_role_fail(self):
        data = {
            "user": {
                "username": "abdul3",
                "email": "abdul3@gmail.com",
                "password": "R@m@_f0rtu9e$",
            },
            "role": "DE",
            "contact_number": "123456789",
        }
        response = self.client.post(self.register, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_role_required_fail(self):
        data = {
            "user": {
                "username": "abdul3",
                "email": "abdul3@gmail.com",
                "password": "R@m@_f0rtu9e$",
            },
            "contact_number": "123456789",
        }
        response = self.client.post(self.register, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_contact_fail(self):
        data = {
            "user": {
                "username": "abdul3",
                "email": "abdul3@gmail.com",
                "password": "R@m@_f0rtu9e$",
            },
            "role": "DEV",
            "contact_number": "1234567891011",
        }
        response = self.client.post(self.register, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestProjectAPI(BaseAPITestCase):
    def test_create_project(self):
        data = {
            "title": "My Project",
            "description": "This is a test project",
            "team_members": [1],
        }
        response = self.client.post('/api/projects/', data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_project_fail(self):
        data = {
            "title": "My Project",
            "description": "This is a test project",
            "team_members": [1],
        }
        response = self.client1.post(
            '/api/projects/', data=data, format="json"
            )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
            )

    def test_get_all_projects_manager(self):
        data = {
            "title": "My Project",
            "description": "This is a test project",
            "team_members": [1],
        }
        response = self.client.get('/api/projects/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_projects_user(self):
        data = {
            "title": "My Project",
            "description": "This is a test project",
            "team_members": [1],
        }
        response = self.client1.get('/api/projects/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_project_detail(self):
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_project_detail(self):
        data = {
            "title": "My Project updated",
            "description": "This is a test project updated",
            "team_members": [1],
        }
        response = self.client.put(
            f'/api/projects/{self.project.id}/',
            data=data,
            format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_project_detail_fail(self):
        data = {
            "title": "My Project updated",
            "description": "This is a test project updated",
            "team_members": [1],
        }
        response = self.client1.put(
            f'/api/projects/{self.project.id}/',
            data=data,
            format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project(self):
        response = self.client.delete(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_project_fail(self):
        response = self.client1.delete(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_member_project(self):
        data = {
            "emails": ["abdul4@gmail.com"]
        }
        response = self.client.post(
            f'/api/projects/{self.project1.id}/add_member/',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_member_project_fail(self):
        data = {
            "emails": ["abdul4@gmail.com", "abdul6@gmail.com"]
        }
        response = self.client.post(
            f'/api/projects/{self.project1.id}/add_member/',
            data=data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_member_project_user_fail(self):
        data = {
            "emails": ["abdul4@gmail.com"]
        }
        response = self.client1.post(
            f'/api/projects/{self.project1.id}/add_member/',
            data=data,
            format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestTaskAPI(BaseAPITestCase):

    def setUp(self):
        return super().setUp()

    def test_create_task_manager(self):
        data = {
            "title": "Task for project id 1",
            "description": "the description of this task",
            "status": "OP",
            "project": 1
        }
        response = self.client.post('/api/tasks/', data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_task_user(self):
        data = {
            "title": "Task for project id 1",
            "description": "the description of this task",
            "status": "OP",
            "project": 1
        }
        response = self.client1.post('/api/tasks/', data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_status_fail(self):
        data = {
            "title": "Task for project id 1",
            "description": "the description of this task",
            "status": "WP",
            "project": 1
        }
        response = self.client.post('/api/tasks/', data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_status_required_fail(self):
        data = {
            "title": "Task for project id 1",
            "description": "the description of this task",
            "project": 1
        }
        response = self.client.post('/api/tasks/', data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_user_fail(self):
        data = {
            "title": "Task for project id 1",
            "description": "the description of this task",
            "status": "OP",
            "project": 1
        }
        response = self.client1.post('/api/tasks/', data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_all_tasks_manager(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_tasks_user(self):
        response = self.client1.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_task_detail(self):
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_task_detail(self):
        data = {
            "title": "Task for project id 1 updated",
            "description": "the description of this task updated",
            "status": "OP",
            "project": 1
        }
        response = self.client.put(
            f'/api/tasks/{self.task.id}/',
            data=data,
            format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_task(self):
        response = self.client.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_task_user_fail(self):
        response = self.client1.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_assignee_task(self):
        data = {
            "emails": ['abdul4@gmail.com']
        }
        response = self.client.post(
            f'/api/tasks/{self.task.id}/assign/',
            data=data,
            format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_assignee_task_assign_fail(self):
        data = {
            "emails": ['abdul5@gmail.com']
        }
        response = self.client.post(
            f'/api/tasks/{self.task.id}/assign/',
            data=data,
            format='json'
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestDocumentAPI(BaseAPITestCase):

    def setUp(self):
        return super().setUp()

    def test_create_document(self):
        file_content = b'This is a test file content.'
        document_file = SimpleUploadedFile("test_document.txt", file_content)
        data = {
            "name": "Test Doc",
            "description": "this is the description",
            "file": document_file,
            "version": "1.0",
            "project": self.project.id
        }
        response = self.client.post(
            '/api/documents/',
            data=data,
            format="multipart"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_documents(self):
        response = self.client.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_documents_user(self):
        response = self.client1.get('/api/documents/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_document_detail(self):
        response = self.client.get(f'/api/documents/{self.document.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_document_detail(self):
        file_content = b'This is a test file content updated.'
        document_file1 = SimpleUploadedFile("test_document.txt", file_content)
        data = {
            "name": "Test Doc updated",
            "description": "this is the description updated",
            "file": document_file1,
            "version": "1.0",
            "project": self.project.id
        }
        response = self.client.put(
            f'/api/documents/{self.document.id}/',
            data=data,
            format="multipart"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_document(self):
        response = self.client.delete(f'/api/documents/{self.document.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TestCommentAPI(BaseAPITestCase):

    def setUp(self):
        return super().setUp()

    def test_create_comment(self):
        data = {
            "text": "This task looks complicated",
            "author": 1,
            "task": 1,
            "project": 1
        }
        response = self.client.post(
            '/api/comments/',
            data=data,
            format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment_fail(self):
        data = {
            "text": "This task looks complicated",
            "author": 2,
            "task": 1,
            "project": 1
        }
        response = self.client.post(
            '/api/comments/',
            data=data,
            format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_comments(self):
        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_comments_user(self):
        response = self.client1.get('/api/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comment_detail(self):
        response = self.client.get(f'/api/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment(self):
        data = {
            "text": "This task looks complicated updated",
            "author": 1,
            "task": 1,
            "project": 1
        }
        response = self.client.put(
            f'/api/comments/{self.comment.id}/',
            data=data,
            format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_comment_fail(self):
        data = {
            "text": "This task looks complicated updated",
            "author": 1,
            "task": 1,
            "project": 2
        }
        response = self.client.put(
            f'/api/comments/{self.comment.id}/',
            data=data,
            format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_comment(self):
        response = self.client.delete(f'/api/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_author_fail(self):
        response = self.client1.delete(f'/api/comments/{self.comment.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
