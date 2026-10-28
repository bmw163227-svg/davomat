from django import template
from django.utils.html import format_html, format_html_join

register = template.Library()

# Barcha ikonkalar shu yerda. Kalit (chapda) shablonlarda ishlatiladi,
# qiymat (o'ngda) iconify.design dagi ikonka nomi.
# Ikonkani almashtirish uchun faqat o'ng tomonni o'zgartiring.
ICONS = {
    # Umumiy
    "logo": "solar:checklist-minimalistic-bold-duotone",
    "lock": "solar:lock-keyhole-minimalistic-bold-duotone",
    "password": "solar:lock-password-bold-duotone",
    "login": "solar:login-2-bold-duotone",
    "logout": "solar:logout-2-bold-duotone",
    "sun": "solar:sun-2-bold-duotone",
    "moon": "solar:moon-stars-bold-duotone",
    "settings": "solar:settings-bold-duotone",
    "panel": "solar:widget-5-bold-duotone",

    # Harakatlar
    "add": "solar:add-circle-bold-duotone",
    "add-student": "solar:user-plus-bold-duotone",
    "edit": "solar:pen-2-bold-duotone",
    "delete": "solar:trash-bin-trash-bold-duotone",
    "save": "solar:diskette-bold-duotone",
    "upload": "solar:upload-minimalistic-bold-duotone",
    "download": "solar:download-minimalistic-bold-duotone",
    "close": "solar:close-circle-linear",
    "back": "solar:arrow-left-linear",
    "prev": "solar:alt-arrow-left-linear",
    "next": "solar:alt-arrow-right-linear",

    # Holatlar
    "present": "solar:check-circle-bold-duotone",
    "absent": "solar:close-circle-bold-duotone",
    "absent-user": "solar:user-cross-bold-duotone",
    "pending": "solar:clock-circle-bold-duotone",
    "info": "solar:info-circle-bold-duotone",
    "warning": "solar:danger-circle-bold-duotone",

    # Bo'limlar
    "groups": "solar:users-group-rounded-bold-duotone",
    "groups-alt": "solar:users-group-two-rounded-bold-duotone",
    "student": "solar:square-academic-cap-bold-duotone",
    "users-admin": "solar:shield-user-bold-duotone",
    "dashboard": "solar:chart-2-bold-duotone",
    "percent": "solar:pie-chart-2-bold-duotone",
    "calendar": "solar:calendar-mark-bold-duotone",
    "month": "solar:calendar-bold-duotone",
    "mark": "solar:clipboard-check-bold-duotone",
    "history": "solar:document-text-bold-duotone",
}

FALLBACK = "solar:question-circle-bold-duotone"


@register.simple_tag
def icon(name, **attrs):
    """
    {% icon "edit" %}
    {% icon "moon" class="i-moon" %}
    {% icon "pending" style="font-size:20px" %}
    {% icon "lucide:pencil" %}   ← ro'yxatda yo'q to'liq nom ham ishlaydi
    """
    icon_id = ICONS.get(name) or (name if ":" in name else FALLBACK)
    extra = format_html_join("", ' {}="{}"', attrs.items())
    return format_html('<iconify-icon icon="{}"{}></iconify-icon>', icon_id, extra)