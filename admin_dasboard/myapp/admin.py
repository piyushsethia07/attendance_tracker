from django.contrib import admin

# Register your models here.
from myapp.models import Class, Teacher, ClassSchedule, UploadFile

class UploadFileAdmin(admin.ModelAdmin):
    list_display = ('file',)

admin.site.register(Class)
admin.site.register(Teacher)
admin.site.register(ClassSchedule)
admin.site.register(UploadFile, UploadFileAdmin)
