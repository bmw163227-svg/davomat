from django.db import models


class Group(models.Model):
    name = models.CharField("Guruh nomi", max_length=100, unique=True)
    description = models.CharField("Izoh", max_length=255, blank=True)
    created_at = models.DateTimeField("Yaratilgan", auto_now_add=True)

    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    full_name = models.CharField("F.I.Sh.", max_length=150)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="students", verbose_name="Guruh"
    )
    phone = models.CharField("Telefon", max_length=20, blank=True)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Talaba"
        verbose_name_plural = "Talabalar"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Attendance(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="attendances", verbose_name="Talaba"
    )
    date = models.DateField("Dars sanasi")
    is_present = models.BooleanField("Qatnashdi", default=True)
    note = models.CharField("Izoh", max_length=255, blank=True)

    class Meta:
        verbose_name = "Davomat"
        verbose_name_plural = "Davomatlar"
        ordering = ["-date", "student__full_name"]
        constraints = [
            models.UniqueConstraint(fields=["student", "date"], name="unique_student_date")
        ]

    def __str__(self):
        holat = "keldi" if self.is_present else "kelmadi"
        return f"{self.student} — {self.date} — {holat}"
# Create your models here.
