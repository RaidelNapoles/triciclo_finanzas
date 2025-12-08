from datetime import datetime
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings
from .base import BaseModel


class Recaudacion(BaseModel):
    fecha = models.DateField(verbose_name="Fecha de recaudación", default=timezone.now)
    monto = models.DecimalField(
        verbose_name="Monto recaudado",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    numero_semana = models.PositiveIntegerField(verbose_name="Semana", blank=True)

    class Meta:
        verbose_name = "Recaudación"
        verbose_name_plural = "Recaudaciones"
        ordering = ["-fecha"]
        indexes = [
            models.Index(fields=["fecha"]),
            models.Index(fields=["numero_semana"]),
        ]

    def __str__(self):
        return f"Fecha: {self.fecha}, Recaudación: $ {self.monto}"

    def save(self, *args, **kwargs):
        fecha_inicio = datetime.strptime(
            settings.RECORDING_START_DATE, "%Y-%m-%d"
        ).date()
        self.numero_semana = (
            self.fecha.isocalendar()[1] - fecha_inicio.isocalendar()[1] + 1
        )
        super().save(*args, **kwargs)

    @property
    def dia_semana(self):
        dias = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes",
            5: "Sábado",
            6: "Domingo",
        }
        return dias[self.fecha.weekday()]
