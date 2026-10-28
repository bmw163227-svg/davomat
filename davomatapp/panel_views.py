from datetime import datetime, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AttendanceEditForm,
    GroupForm,
    StudentEditForm,
    UserCreateForm,
    UserEditForm,
)
from .models import Attendance, Group, Student

User = get_user_model()
PER_PAGE = 20


# ------------------------------------------------------------- Ruxsatlar
def staff_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper


def superuser_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapper


def _paginate(request, qs, per_page=PER_PAGE):
    page = Paginator(qs, per_page).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return page, params.urlencode()


def _percent(present, total):
    return round(present * 100 / total) if total else None


# ------------------------------------------------------------- Bosh sahifa
@staff_required
def dashboard(request):
    today = timezone.localdate()
    week_start = today - timedelta(days=6)

    today_qs = Attendance.objects.filter(date=today, student__is_active=True)
    t_present = today_qs.filter(is_present=True).count()
    t_absent = today_qs.filter(is_present=False).count()
    active_students = Student.objects.filter(is_active=True).count()

    by_day = {
        r["date"]: r
        for r in Attendance.objects.filter(date__gte=week_start, date__lte=today)
        .values("date")
        .annotate(
            present=Count("id", filter=Q(is_present=True)),
            absent=Count("id", filter=Q(is_present=False)),
        )
    }
    week = []
    for i in range(7):
        d = week_start + timedelta(days=i)
        row = by_day.get(d, {})
        p, a = row.get("present", 0), row.get("absent", 0)
        week.append({"date": d, "present": p, "absent": a, "percent": _percent(p, p + a)})

    month_stats = {
        r["student__group_id"]: r
        for r in Attendance.objects.filter(
            date__year=today.year, date__month=today.month, student__is_active=True
        )
        .values("student__group_id")
        .annotate(present=Count("id", filter=Q(is_present=True)), total=Count("id"))
    }
    groups = list(
        Group.objects.annotate(
            student_count=Count("students", filter=Q(students__is_active=True))
        )
    )
    for g in groups:
        s = month_stats.get(g.id, {})
        g.month_percent = _percent(s.get("present", 0), s.get("total", 0))

    recent = Attendance.objects.select_related("student", "student__group")[:8]

    return render(
        request,
        "davomatapp/panel/dashboard.html",
        {
            "section": "dashboard",
            "today": today,
            "groups_count": len(groups),
            "students_count": Student.objects.count(),
            "active_students": active_students,
            "records_count": Attendance.objects.count(),
            "t_present": t_present,
            "t_absent": t_absent,
            "t_unmarked": max(active_students - t_present - t_absent, 0),
            "t_percent": _percent(t_present, t_present + t_absent),
            "week": week,
            "groups": groups,
            "recent": recent,
        },
    )


# ------------------------------------------------------------- Guruhlar
@staff_required
def groups(request):
    q = request.GET.get("q", "").strip()
    qs = Group.objects.annotate(
        student_count=Count("students"),
        active_count=Count("students", filter=Q(students__is_active=True)),
    )
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    page, qs_params = _paginate(request, qs)
    return render(
        request,
        "davomatapp/panel/groups.html",
        {"section": "groups", "page": page, "qs": qs_params, "q": q},
    )


@staff_required
def group_edit(request, pk=None):
    group = get_object_or_404(Group, pk=pk) if pk else None
    form = GroupForm(request.POST or None, instance=group)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        messages.success(request, f"“{saved.name}” guruhi saqlandi.")
        return redirect("panel_groups")
    return render(
        request,
        "davomatapp/panel/form.html",
        {
            "section": "groups",
            "form": form,
            "title": f"Guruhni tahrirlash: {group.name}" if group else "Yangi guruh",
            "back_url": reverse("panel_groups"),
            "delete_url": reverse("panel_group_delete", args=[group.pk]) if group else None,
            "delete_warning": "Guruh, undagi barcha talabalar va ularning davomat yozuvlari o'chiriladi.",
        },
    )


@staff_required
@require_POST
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    name = group.name
    group.delete()
    messages.success(request, f"“{name}” guruhi o'chirildi.")
    return redirect("panel_groups")


# ------------------------------------------------------------- Talabalar
@staff_required
def students(request):
    q = request.GET.get("q", "").strip()
    group_id = request.GET.get("guruh", "")
    status = request.GET.get("holat", "")

    qs = Student.objects.select_related("group").annotate(
        present_count=Count("attendances", filter=Q(attendances__is_present=True)),
        absent_count=Count("attendances", filter=Q(attendances__is_present=False)),
    )
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(phone__icontains=q))
    if group_id.isdigit():
        qs = qs.filter(group_id=group_id)
    if status == "active":
        qs = qs.filter(is_active=True)
    elif status == "inactive":
        qs = qs.filter(is_active=False)

    page, qs_params = _paginate(request, qs)
    page.object_list = list(page.object_list)
    for s in page.object_list:
        s.percent = _percent(s.present_count, s.present_count + s.absent_count)

    return render(
        request,
        "davomatapp/panel/students.html",
        {
            "section": "students",
            "page": page,
            "qs": qs_params,
            "q": q,
            "group_id": group_id,
            "status": status,
            "all_groups": Group.objects.all(),
        },
    )


@staff_required
def student_edit(request, pk=None):
    student = get_object_or_404(Student, pk=pk) if pk else None
    initial = {}
    if not student and request.GET.get("guruh", "").isdigit():
        initial["group"] = request.GET["guruh"]
    form = StudentEditForm(request.POST or None, instance=student, initial=initial)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        messages.success(request, f"{saved.full_name} saqlandi.")
        return redirect("panel_students")
    return render(
        request,
        "davomatapp/panel/form.html",
        {
            "section": "students",
            "form": form,
            "title": f"Talabani tahrirlash: {student.full_name}" if student else "Yangi talaba",
            "back_url": reverse("panel_students"),
            "delete_url": reverse("panel_student_delete", args=[student.pk]) if student else None,
            "delete_warning": "Talaba va uning barcha davomat yozuvlari o'chiriladi. Tarixni saqlash uchun o'chirmasdan “Faol” belgisini oling.",
        },
    )


@staff_required
@require_POST
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    name = student.full_name
    student.delete()
    messages.success(request, f"{name} o'chirildi.")
    return redirect("panel_students")


# ------------------------------------------------------------- Davomat yozuvlari
@staff_required
def attendance_list(request):
    q = request.GET.get("q", "").strip()
    group_id = request.GET.get("guruh", "")
    status = request.GET.get("holat", "")
    date_value = request.GET.get("sana", "")

    qs = Attendance.objects.select_related("student", "student__group")
    if q:
        qs = qs.filter(student__full_name__icontains=q)
    if group_id.isdigit():
        qs = qs.filter(student__group_id=group_id)
    if status == "present":
        qs = qs.filter(is_present=True)
    elif status == "absent":
        qs = qs.filter(is_present=False)
    try:
        qs = qs.filter(date=datetime.strptime(date_value, "%Y-%m-%d").date())
    except ValueError:
        date_value = ""

    totals = qs.aggregate(
        present=Count("id", filter=Q(is_present=True)),
        absent=Count("id", filter=Q(is_present=False)),
    )
    page, qs_params = _paginate(request, qs, per_page=30)
    return render(
        request,
        "davomatapp/panel/attendance.html",
        {
            "section": "attendance",
            "page": page,
            "qs": qs_params,
            "q": q,
            "group_id": group_id,
            "status": status,
            "date_value": date_value,
            "totals": totals,
            "all_groups": Group.objects.all(),
        },
    )


@staff_required
def attendance_edit(request, pk):
    record = get_object_or_404(Attendance.objects.select_related("student"), pk=pk)
    form = AttendanceEditForm(request.POST or None, instance=record)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Davomat yozuvi yangilandi.")
        return redirect("panel_attendance")
    return render(
        request,
        "davomatapp/panel/form.html",
        {
            "section": "attendance",
            "form": form,
            "title": "Davomat yozuvini tahrirlash",
            "subtitle": f"{record.student.full_name} · {record.date:%d.%m.%Y}",
            "back_url": reverse("panel_attendance"),
            "delete_url": reverse("panel_attendance_delete", args=[record.pk]),
            "delete_warning": "Bu kun uchun davomat yozuvi o'chiriladi (jadvalda katak bo'sh bo'lib qoladi).",
        },
    )


@staff_required
@require_POST
def attendance_delete(request, pk):
    get_object_or_404(Attendance, pk=pk).delete()
    messages.success(request, "Davomat yozuvi o'chirildi.")
    return redirect("panel_attendance")


# ------------------------------------------------------------- Foydalanuvchilar
@superuser_required
def users(request):
    q = request.GET.get("q", "").strip()
    qs = User.objects.all().order_by("-is_superuser", "-is_staff", "username")
    if q:
        qs = qs.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    page, qs_params = _paginate(request, qs)
    return render(
        request,
        "davomatapp/panel/users.html",
        {"section": "users", "page": page, "qs": qs_params, "q": q},
    )


@superuser_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"{user.username} foydalanuvchisi yaratildi.")
        return redirect("panel_users")
    return render(
        request,
        "davomatapp/panel/user_form.html",
        {"section": "users", "form": form, "title": "Yangi foydalanuvchi"},
    )


@superuser_required
def user_edit(request, pk):
    target = get_object_or_404(User, pk=pk)
    is_self = target.pk == request.user.pk
    form = UserEditForm(instance=target, lock=is_self)
    pw_form = SetPasswordForm(target)

    if request.method == "POST":
        if "set_password" in request.POST:
            pw_form = SetPasswordForm(target, request.POST)
            if pw_form.is_valid():
                pw_form.save()
                if is_self:
                    update_session_auth_hash(request, target)
                messages.success(request, "Parol almashtirildi.")
                return redirect("panel_user_edit", pk=target.pk)
        else:
            form = UserEditForm(request.POST, instance=target, lock=is_self)
            if form.is_valid():
                form.save()
                messages.success(request, f"{target.username} ma'lumotlari saqlandi.")
                return redirect("panel_users")

    return render(
        request,
        "davomatapp/panel/user_form.html",
        {
            "section": "users",
            "form": form,
            "pw_form": pw_form,
            "target": target,
            "is_self": is_self,
            "title": f"Foydalanuvchi: {target.username}",
            "delete_url": None if is_self else reverse("panel_user_delete", args=[target.pk]),
        },
    )


@superuser_required
@require_POST
def user_delete(request, pk):
    target = get_object_or_404(User, pk=pk)
    if target.pk == request.user.pk:
        messages.error(request, "O'zingizni o'chira olmaysiz.")
        return redirect("panel_users")
    name = target.username
    target.delete()
    messages.success(request, f"{name} o'chirildi.")
    return redirect("panel_users")