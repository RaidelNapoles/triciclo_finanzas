from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Avg, Count
from django.contrib import messages
from django.utils import timezone
import json
import datetime
import matplotlib

from finanzas_app.models.ingresos import Recaudacion
from finanzas_app.services.dashboard_service import GeneradorGraficos
from finanzas_app.services.estadisticas_service import EstadisticaService


import io
import base64
import pandas as pd


def index(request):
    """Página principal con el dashboard"""
    # Obtener estadísticas
    estadisticas = EstadisticaService.obtener_estadisticas()
    por_semana = EstadisticaService.obtener_por_semana()
    por_mes = EstadisticaService.obtener_por_mes()
    por_dia_semana = EstadisticaService.obtener_por_dia_semana()

    # Últimos registros
    ultimos_registros = Recaudacion.objects.all().order_by("-fecha")[:10]

    # Generar gráficos
    grafico_semana = GeneradorGraficos.crear_grafico_semanal(list(por_semana.values()))
    grafico_mes = GeneradorGraficos.crear_grafico_mensual(list(por_mes.values()))
    grafico_dia_semana = GeneradorGraficos.crear_grafico_diario(por_dia_semana)
    grafico_promedio_dia_semana = GeneradorGraficos.crear_grafico_promedio_diario(
        por_dia_semana
    )

    context = {
        "estadisticas": estadisticas,
        "por_semana": por_semana,
        "por_mes": por_mes,
        "por_dia_semana": por_dia_semana,
        "ultimos_registros": ultimos_registros,
        "grafico_semana": grafico_semana,
        "grafico_mes": grafico_mes,
        "grafico_dia_semana": grafico_dia_semana,
        "grafico_promedio_dia_semana": grafico_promedio_dia_semana,
    }

    return render(request, "finanzas_app/dashboard.html", context)
