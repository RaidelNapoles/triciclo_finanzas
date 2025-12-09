import datetime
from django.shortcuts import render
from finanzas_app.models.ingresos import Recaudacion
from finanzas_app.services.estadisticas_service import EstadisticaService


def deuda_semanal(request):
    contexto = EstadisticaService.obtener_deuda_semanal()
    return render(request, "finanzas_app/deuda_semanal.html", contexto)
