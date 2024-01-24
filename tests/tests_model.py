from app.models import Comment, CustomUser, Document, Profile, Project, Task
from django.test import TestCase


class BaseTestModel(TestCase):
    def setUp(self):
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


class TestCustomUser(BaseTestModel):

    def setUp(self):
        return super().setUp()

    def test_user(self):
        self.assertEqual(self.user.email, "abdul4@gmail.com")


class TestProfile(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_profile(self):
        self.assertEqual(self.profile.role, 'MA')


class TestProject(BaseTestModel):

    def setUp(self) -> None:
        return super().setUp()

    def test_project(self):
        self.assertEqual(self.project.title, 'test project')


class TestTask(BaseTestModel):

    def setUp(self):
        return super().setUp()

    def test_task(self):
        self.assertEqual(self.task.description, 'test task description')


class TestDocument(BaseTestModel):

    def setUp(self):
        return super().setUp()

    def test_docuement(self):
        self.assertEqual(self.document.name, 'test name')


class TestComment(BaseTestModel):

    def setUp(self):
        return super().setUp()

    def test_comment(self):
        self.assertEqual(self.comment.text, 'test comment')
