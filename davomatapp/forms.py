from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Attendance, Group, Student

User = get_user_model()


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "description"]


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["full_name", "phone", "is_active"]


class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["full_name", "group", "phone", "is_active"]


class ImportForm(forms.Form):
    file = forms.FileField(label="Fayl (.xlsx, .csv, .txt)")

    def clean_file(self):
        f = self.cleaned_data["file"]
        if not f.name.lower().endswith((".xlsx", ".csv", ".txt")):
            raise forms.ValidationError("Faqat .xlsx, .csv yoki .txt fayl yuklang.")
        if f.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Fayl hajmi 2 MB dan oshmasligi kerak.")
        return f


class AttendanceEditForm(forms.ModelForm):
    """Davomat yozuvida faqat holat va izoh o'zgaradi (talaba va sana qat'iy)."""

    class Meta:
        model = Attendance
        fields = ["is_present", "note"]


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "is_staff")
        labels = {
            "username": "Login",
            "first_name": "Ism",
            "last_name": "Familiya",
            "is_staff": "Admin (boshqaruv paneliga kirish huquqi)",
        }
        help_texts = {
            "username": "",
            "is_staff": "Belgilanmasa, oddiy ustoz bo'ladi: faqat davomat bilan ishlaydi.",
        }


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "is_active", "is_staff")
        labels = {
            "username": "Login",
            "first_name": "Ism",
            "last_name": "Familiya",
            "is_active": "Faol (tizimga kira oladi)",
            "is_staff": "Admin (boshqaruv paneliga kirish huquqi)",
        }
        help_texts = {"username": ""}

    def __init__(self, *args, lock=False, **kwargs):
        super().__init__(*args, **kwargs)
        if lock:  # o'zini bloklab qo'yishdan saqlash
            self.fields["is_active"].disabled = True
            self.fields["is_staff"].disabled = True