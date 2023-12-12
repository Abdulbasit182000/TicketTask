from django.contrib import admin

from .models import Comment, CustomUser, Document, Profile, Project, Task

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Comment)
