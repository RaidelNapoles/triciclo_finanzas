# ingresos/vistas.py (agregar esta función)
"""
Vista para mostrar la tabla semanal de recaudaciones.
"""


import datetime
from django.shortcuts import render
from finanzas_app.models.ingresos import Recaudacion
from finanzas_app.services.estadisticas_service import EstadisticaService
from finanzas_app.services.tablas import ProcesadorTablaSemanal


def tabla_semanal(request):
    """
    Muestra los ingresos en formato tabular por semana y día.

    Estructura:
    - Filas: Números de semana
    - Columnas: Días de la semana (L-D)
    - Última columna: Total semanal
    - Última fila: Total por día
    - Última celda: Total general
    """
    # Obtener todos los ingresos
    ingresos = Recaudacion.objects.all()

    # Procesar datos para la tabla
    datos_tabla = ProcesadorTablaSemanal.crear_tabla_semanal(ingresos)

    # Obtener estadísticas adicionales
    estadisticas = EstadisticaService.obtener_estadisticas()

    # Obtener últimas semanas para filtro
    ultimas_semanas = (
        list(datos_tabla["semanas"][-10:]) if datos_tabla["semanas"] else []
    )

    contexto = {
        "datos_tabla": datos_tabla,
        "estadisticas": estadisticas,
        "ultimas_semanas": ultimas_semanas,
        "hoy": datetime.datetime.today(),
    }

    print(contexto)

    return render(request, "finanzas_app/tabla_semanal.html", contexto)


def tabla_semanal_filtrada(request, semana_inicio=None, semana_fin=None):
    """
    Muestra tabla semanal filtrada por rango de semanas.

    Args:
        semana_inicio (int): Primera semana a mostrar
        semana_fin (int): Última semana a mostrar
    """
    ingresos = Recaudacion.objetos.all()

    # Aplicar filtros de semana si se proporcionan
    if semana_inicio and semana_fin:
        ingresos = ingresos.filter(
            numero_semana__gte=semana_inicio, numero_semana__lte=semana_fin
        )

    datos_tabla = ProcesadorTablaSemanal.crear_tabla_semanal(ingresos)

    contexto = {
        "datos_tabla": datos_tabla,
        "semana_inicio": semana_inicio,
        "semana_fin": semana_fin,
        "filtrado": True if semana_inicio and semana_fin else False,
    }

    return render(request, "ingresos/tabla_semanal_filtrada.html", contexto)


def exportar_tabla_excel(request):
    """
    Exporta la tabla semanal a formato Excel.
    """
    from django.http import HttpResponse
    import pandas as pd
    from io import BytesIO

    # Obtener datos
    ingresos = Recaudacion.objetos.all()
    datos_tabla = ProcesadorTablaSemanal.crear_tabla_semanal(ingresos)

    # Crear DataFrame
    datos_excel = []
    dias = datos_tabla["dias"] + ["TOTAL SEMANA", "%"]

    for semana_num in datos_tabla["semanas"]:
        semana_data = datos_tabla["tabla"][semana_num]
        fila = [semana_num]

        # Agregar datos por día
        for dia in datos_tabla["dias"]:
            valor = semana_data["datos"][dia]
            fila.append(float(valor) if valor > 0 else "")

        # Agregar total semanal y porcentaje
        total_semana = datos_tabla["totales_semanas"][semana_num]["total"]
        porcentaje = datos_tabla["totales_semanas"][semana_num]["porcentaje"]
        fila.extend([float(total_semana), f"{porcentaje}%"])

        datos_excel.append(fila)

    # Agregar fila de totales por día
    fila_totales = ["TOTAL DÍA"]
    for dia in datos_tabla["dias"]:
        total = datos_tabla["totales_dias"][dia]["total"]
        fila_totales.append(float(total))

    # Agregar total general y celda vacía
    fila_totales.extend([float(datos_tabla["total_general"]), ""])
    datos_excel.append(fila_totales)

    # Crear DataFrame
    df = pd.DataFrame(datos_excel, columns=["Semana"] + dias)

    # Crear respuesta Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Tabla Semanal", index=False)

    output.seek(0)

    # Configurar respuesta HTTP
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = (
        'attachment; filename="tabla_semanal_ingresos.xlsx"'
    )

    return response
