from django.contrib import admin

from grades.models import *

# Register your models here.
admin.site.register(Grade)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(WorkType)
