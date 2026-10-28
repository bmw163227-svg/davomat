from django.contrib import admin

from .models import Attendance, Group, Student


class StudentInline(admin.TabularInline):
    model = Student
    extra = 1


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)
    inlines = [StudentInline]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "group", "phone", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("full_name", "phone")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "is_present", "note")
    list_filter = ("date", "is_present", "student__group")
    search_fields = ("student__full_name",)
    date_hierarchy = "date"
# Register your models here.
