from app.models import Comment, CustomUser, Document, Profile, Project, Task
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class TestAPI(APITestCase):
    register = "/api/register/"
    login = "/api/login/"

    def setUp(self):
        self.user = CustomUser.objects.create(
            email="abdul4@gmail.com", username="abdul"
        )
        self.user.set_password("123456")
        self.user.save

        self.profile = Profile.objects.create(
            user=self.user, role="MA", contact_number="123456789"
        )
        self.profile.save()

        self.project = Project.objects.create(
            title="test project",
            description="test description",
        )
        self.project.save()

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
