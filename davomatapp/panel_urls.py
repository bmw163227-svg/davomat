from django.urls import path

from . import panel_views as v

urlpatterns = [
    path("", v.dashboard, name="panel_dashboard"),

    path("guruhlar/", v.groups, name="panel_groups"),
    path("guruhlar/yangi/", v.group_edit, name="panel_group_add"),
    path("guruhlar/<int:pk>/", v.group_edit, name="panel_group_edit"),
    path("guruhlar/<int:pk>/ochirish/", v.group_delete, name="panel_group_delete"),

    path("talabalar/", v.students, name="panel_students"),
    path("talabalar/yangi/", v.student_edit, name="panel_student_add"),
    path("talabalar/<int:pk>/", v.student_edit, name="panel_student_edit"),
    path("talabalar/<int:pk>/ochirish/", v.student_delete, name="panel_student_delete"),

    path("davomat/", v.attendance_list, name="panel_attendance"),
    path("davomat/<int:pk>/", v.attendance_edit, name="panel_attendance_edit"),
    path("davomat/<int:pk>/ochirish/", v.attendance_delete, name="panel_attendance_delete"),

    path("foydalanuvchilar/", v.users, name="panel_users"),
    path("foydalanuvchilar/yangi/", v.user_create, name="panel_user_add"),
    path("foydalanuvchilar/<int:pk>/", v.user_edit, name="panel_user_edit"),
    path("foydalanuvchilar/<int:pk>/ochirish/", v.user_delete, name="panel_user_delete"),
]