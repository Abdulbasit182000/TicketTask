from rest_framework import serializers

from .models import Comment, CustomUser, Document, Profile, Project, Task


class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        if data["email"]:
            if CustomUser.objects.filter(email=data["email"]).exists():
                raise serializers.ValidationError("email is taken")

        if data["username"]:
            if CustomUser.objects.filter(username=data["username"]).exists():
                raise serializers.ValidationError("username is taken")

        if data["password"]:
            x = data["password"]
            l, u, p, d = 0, 0, 0, 0
            if len(x) >= 8:
                for i in x:
                    if i.islower():
                        l += 1
                    if i.isupper():
                        u += 1
                    if i.isdigit():
                        d += 1
                    if i == "@" or i == "$" or i == "_":
                        p += 1
            w = l + p + u + d
            if l >= 1 and u >= 1 and p >= 1 and d >= 1 and w == len(x):
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
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ["user", "role", "contact_number"]
        depth = 1

    def validate(self, data):
        if data.get("role", None):
            if data["role"] != "QA" and data["role"] != "MA":
                if data["role"] != "DEV":
                    raise serializers.ValidationError("Role is not correct")
        else:
            raise serializers.ValidationError("Role is required")

        if data["contact_number"]:
            if len(data["contact_number"]) > 12:
                raise serializers.ValidationError("number not right length")

        return data

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        user = UserSerializer().create(user_data)
        Profile.objects.create(user=user, **validated_data)
        return validated_data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        if data["email"]:
            if CustomUser.objects.filter(email=data["email"]).exists():
                user = CustomUser.objects.get(email=data["email"])
                if data["password"]:
                    if user.check_password(data["password"]):
                        pass
                    else:
                        raise serializers.ValidationError("incorrect password")
            else:
                raise serializers.ValidationError("Email does not exist")
        return data


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["title", "description", "team_members"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["assignee"]

    def validate(self, data):
        status = data.get("status", None)

        if not status:
            raise serializers.ValidationError("Status is required")

        valid_statuses = ["OP", "REV", "WOR", "AWAIT", "WAIT"]

        if status not in valid_statuses:
            raise serializers.ValidationError("Status is not correct")

        return data


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
