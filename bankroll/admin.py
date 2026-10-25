from django.contrib import admin

from .models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "host",
        "format",
        "type",
        "stakes",
        "session_start",
        "session_end",
        "buyin",
        "buyout",
        "profit",
    )
    list_filter = ("format", "type")
    search_fields = ("host", "stakes")
