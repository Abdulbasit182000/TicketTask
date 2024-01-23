from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Document, Profile, Project, Task
from .permissions import IsManager
from .serializers import (CommentSerializer, DocumentSerializer,
                          ProfileSerializer, ProjectSerializer,
                          RegisterSerializer, TaskSerializer)


class RegisterAPI(APIView):
    def post(self, request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": True, "message": "Profile Created"},
                status.HTTP_201_CREATED,
            )
        return Response(
            {"status": False, "message": serializer.errors},
            status.HTTP_400_BAD_REQUEST,
        )


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action in ["list"]:
            user = self.request.user
            profile = Profile.objects.filter(user=user)
            queryset = profile
        else:
            profile = Profile.objects.all()
            queryset = profile
        return queryset

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProjectViewset(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "document", "task"]:
            permission_classes = [IsAuthenticated]
            print('done')

        else:
            permission_classes = [IsManager]
            print('auth')

        return [
            permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            user = self.request.user
            profile = Profile.objects.get(user=user)
            if profile.role == "MA":
                queryset = Project.objects.all()
            else:
                queryset = Project.objects.filter(team_members__user=user)
        else:
            queryset = Project.objects.all()

        return queryset

    def create(self, request):
        data = request.data
        print(data)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
         instance,
         data=request.data,
         partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk):
        user = request.user
        profile = Profile.objects.get(user=user)
        if profile.role == "MA":
            emails = request.data.get("emails", [])
            instance = self.get_object()
            for email in emails:
                profile = Profile.objects.filter(user__email=email)
                if profile:
                    profile = profile.first()
                    if instance.team_members.filter(id=profile.id).exists():
                        pass
                    else:
                        instance.team_members.add(profile)
                else:
                    return Response(
                        {"status": False, "message": "profile not exist"},
                        status.HTTP_400_BAD_REQUEST,
                    )
            instance.save()
            return Response(
                {"status": True, "message": "Team members added"},
                status.HTTP_200_OK,
            )
        else:
            return Response(
                {"status": False, "message": "you dont have acess rights"},
                status.HTTP_403_FORBIDDEN,
            )

    @action(detail=True, methods=["get"])
    def task(self, request, pk):
        instance = self.get_object()
        tasks = Task.objects.filter(project=instance)
        page = self.paginate_queryset(tasks)
        if page is not None:
            serrializer = TaskSerializer(page, many=True)
            return self.get_paginated_response(serrializer.data)

        serrializer = TaskSerializer(tasks, many=True)
        return Response(serrializer.data)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def document(self, request, pk):
        instance = self.get_object()
        print(request.user)

        if not request.user.is_authenticated:
            return Response(
                {"status": False, "message": "Authentication required"},
                status.HTTP_401_UNAUTHORIZED,
            )

        profile = Profile.objects.get(user=request.user)
        members = instance.team_members.all()

        if profile.role == "MA" or profile in members:
            documents = Document.objects.filter(project=instance)
            page = self.paginate_queryset(documents)
            if page is not None:
                serrializer = DocumentSerializer(page, many=True)
                return self.get_paginated_response(serrializer.data)

            serrializer = DocumentSerializer(documents, many=True)
            return Response(serrializer.data)

        else:
            return Response(
                {"status": False, "message": "You don't have access rights"},
                status.HTTP_403_FORBIDDEN,
            )


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "comment"]:
            permission_classes = [IsAuthenticated]

        else:
            permission_classes = [IsManager]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            user = self.request.user
            profile = Profile.objects.get(user=user)
            if profile.role == "MA":
                queryset = Task.objects.all()
            else:
                queryset = Task.objects.filter(assignee__user=user)
        else:
            queryset = Task.objects.all()

        return queryset

    def create(self, request):
        data = request.data
        user = request.user
        profile = Profile.objects.get(user=user)
        if profile.role == "MA":
            pass
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        print(request.data)
        partial = kwargs.pop("partial", False)
        user = request.user
        profile = Profile.objects.get(user=user)
        if profile.role == "MA":
            pass
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    @action(detail=True, methods=["post"])
    def assign(self, request, pk):
        user = request.user
        profile = Profile.objects.get(user=user)
        if profile.role == "MA":
            emails = request.data.get("emails", [])
            instance = self.get_object()
            for email in emails:
                profile = Profile.objects.filter(user__email=email)
                if profile:
                    profile = profile.first()
                    if instance.assignee.filter(id=profile.id).exists():
                        pass
                    else:
                        p = instance.project.team_members.values_list(
                            "user__email", flat=True
                        )
                        if email in p:
                            instance.assignee.add(profile)
                        else:
                            return Response(
                                {
                                    "status": False,
                                    "message": "inccorect users",
                                },
                                status.HTTP_400_BAD_REQUEST,
                            )
                else:
                    return Response(
                        {
                            "status": False,
                            "message": "inccorect users",
                        },
                        status.HTTP_400_BAD_REQUEST,
                    )
            instance.save()
            return Response(
                {"status": True, "message": "assignee added"},
                status.HTTP_200_OK,
            )

    @action(detail=True, methods=["get"])
    def comment(self, request, pk):
        instance = self.get_object()
        comments = Comment.objects.filter(task=instance)
        page = self.paginate_queryset(comments)
        if page is not None:
            serrializer = CommentSerializer(page, many=True)
            return self.get_paginated_response(serrializer.data)

        serrializer = CommentSerializer(comments, many=True)
        return Response(serrializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            user = self.request.user
            profile = Profile.objects.get(user=user)
            if profile.role == "MA":
                queryset = Document.objects.all()
            else:
                queryset = Document.objects.filter(
                    project__team_members__user=user)
        else:
            queryset = Document.objects.all()

        return queryset

    def create(self, request):
        data = request.data
        print(data)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            user = self.request.user
            profile = Profile.objects.get(user=user)
            if profile.role == "MA":
                queryset = Comment.objects.all()
            else:
                queryset = Comment.objects.filter(
                    project__team_members__user=user)
        else:
            queryset = Comment.objects.all()

        return queryset

    def create(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        profile = Profile.objects.get(user=user)
        if instance.author == profile:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
