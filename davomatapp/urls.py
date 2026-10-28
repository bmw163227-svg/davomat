from django.urls import path

from . import views

urlpatterns = [
    path("", views.group_list, name="group_list"),
    path("guruh/yangi/", views.group_create, name="group_create"),
    path("guruh/<int:pk>/", views.group_detail, name="group_detail"),
    path("guruh/<int:pk>/talaba-qoshish/", views.student_create, name="student_create"),
    path("guruh/<int:pk>/import/", views.group_import, name="group_import"),
    path("guruh/<int:pk>/davomat/", views.mark_attendance, name="mark_attendance"),
    path("guruh/<int:pk>/export.csv", views.export_csv, name="export_csv"),
    path("talaba/<int:pk>/", views.student_detail, name="student_detail"),
    path("talaba/<int:pk>/statistika/", views.student_stats, name="student_stats"),
    path("talaba/<int:pk>/tahrirlash/", views.student_update, name="student_update"),
    path("talaba/<int:pk>/ochirish/", views.student_delete, name="student_delete"),
]