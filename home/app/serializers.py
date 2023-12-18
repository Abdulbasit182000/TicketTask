from rest_framework import serializers

from .models import Comment, CustomUser, Document, Profile, Project, Task


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        if CustomUser.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("email is taken")

        if CustomUser.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError("username is taken")

        x = data["password"]
        arr = [0, 0, 0, 0]
        if len(x) >= 8:
            for i in x:
                if i.islower():
                    arr[0] += 1
                if i.isupper():
                    arr[1] += 1
                if i.isdigit():
                    arr[2] += 1
                if i == "@" or i == "$" or i == "_":
                    arr[3] += 1
        w = sum(arr)
        if min(arr) > 0 and w == len(x):
            pass
        else:
            raise serializers.ValidationError(
                "Password Does not match the requirements"
            )
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data["username"], email=validated_data["email"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class RegisterSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Profile
        fields = ["user", "role", "contact_number"]
        depth = 1
        extra_kwargs = {
            'role': {'required': True},
            'contact_number': {'required': True},
        }

    def validate(self, data):
        if len(data["contact_number"]) > 12:
            raise serializers.ValidationError("number not right length")

        return data

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = UserSerializer().create(user_data)
        Profile.objects.create(user=user, **validated_data)
        return validated_data


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["title", "description", "team_members"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["assignee"]
        extra_kwargs = {
            'status': {'required': True},
        }


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

    def validate(self, data):
        author = data.get("author")
        task = data.get("task")
        project = data.get("project")

        if task.project == project:
            pass
        else:
            raise serializers.ValidationError("project is not part of task")

        users = project.team_members.all()  # Retrieve all team members
        if users.filter(pk=author.pk).exists():
            pass
        else:
            raise serializers.ValidationError("author is not part of project")

        return data
