from django.contrib import admin
from django.contrib.admin.decorators import register
from .models.ingresos import Recaudacion


@register(Recaudacion)
class RecaudacionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "numero_semana", "dia_semana", "monto")
    list_filter = ("fecha", "numero_semana")
    date_hierarchy = "fecha"
    ordering = ("-fecha",)

    fieldsets = (
        ("Información Principal", {"fields": ("fecha", "monto")}),
        (
            "Información calculada",
            {"fields": ("numero_semana",), "classes": ("collapse")},
        ),
    )
