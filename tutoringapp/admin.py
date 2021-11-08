from django.contrib import admin
from . import models

admin.site.register(models.UserModel)
admin.site.register(models.ClassModel)
admin.site.register(models.TeacherModel)
admin.site.register(models.StudentModel)
