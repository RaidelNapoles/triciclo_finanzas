# ingresos/tablas.py
"""
Módulo para procesar datos en formato tabular semanal.
Organiza los ingresos por semana (filas) y días (columnas).
"""

from django.utils import timezone
from decimal import Decimal
import datetime
from collections import OrderedDict


class ProcesadorTablaSemanal:
    """
    Procesa los datos de ingresos en formato tabular.

    Estructura:
    - Filas: Semanas (1, 2, 3, ...)
    - Columnas: Días de la semana (Lunes a Domingo)
    - Celda: Ingreso del día específico
    - Totales: Por semana y por día
    """

    @staticmethod
    def crear_tabla_semanal(ingresos):
        """
        Crea una tabla organizada por semanas y días.

        Args:
            ingresos (QuerySet): Todos los registros de ingresos

        Returns:
            dict: Estructura de datos para la tabla
        """
        if not ingresos.exists():
            return {
                "tabla": {},
                "semanas": [],
                "dias": [],
                "totales_semanas": {},
                "totales_dias": {},
                "total_general": Decimal("0.00"),
                "promedio_diario": Decimal("0.00"),
            }

        # Ordenar por fecha
        ingresos_ordenados = ingresos.order_by("fecha")

        # Obtener lista de días de la semana
        dias_semana = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]

        # Inicializar estructura
        tabla = OrderedDict()
        totales_semanas = {}
        totales_dias = {dia: Decimal("0.00") for dia in dias_semana}
        total_general = Decimal("0.00")

        # Procesar cada registro
        for ingreso in ingresos_ordenados:
            semana = ingreso.numero_semana
            dia = ingreso.dia_semana

            # Inicializar semana si no existe
            if semana not in tabla:
                tabla[semana] = {
                    "semana_numero": semana,
                    "datos": {dia: Decimal("0.00") for dia in dias_semana},
                    "fecha_inicio": ingreso.fecha,
                    "fecha_fin": ingreso.fecha,
                }
                totales_semanas[semana] = Decimal("0.00")

            # Actualizar datos de la semana
            tabla[semana]["datos"][dia] = ingreso.monto

            # Actualizar totales
            totales_semanas[semana] += ingreso.monto
            totales_dias[dia] += ingreso.monto
            total_general += ingreso.monto

            # Actualizar rango de fechas
            if ingreso.fecha < tabla[semana]["fecha_inicio"]:
                tabla[semana]["fecha_inicio"] = ingreso.fecha
            if ingreso.fecha > tabla[semana]["fecha_fin"]:
                tabla[semana]["fecha_fin"] = ingreso.fecha

        # Calcular promedio diario
        dias_registrados = sum(
            1
            for semana in tabla.values()
            for valor in semana["datos"].values()
            if valor >= 0
        )
        promedio_diario = (
            total_general / dias_registrados
            if dias_registrados > 0
            else Decimal("0.00")
        )

        # Ordenar semanas
        semanas_ordenadas = sorted(tabla.keys())
        print(f"Semanas ordenadas: {semanas_ordenadas}")

        # Calcular totales por día con porcentaje
        totales_dias_con_porcentaje = {}
        for dia, total in totales_dias.items():
            porcentaje = (total / total_general * 100) if total_general > 0 else 0
            totales_dias_con_porcentaje[dia] = {
                "total": total,
                "porcentaje": round(porcentaje, 1),
            }

        # Calcular totales por semana con porcentaje
        totales_semanas_con_porcentaje = {}
        for semana, total in totales_semanas.items():
            porcentaje = (total / total_general * 100) if total_general > 0 else 0
            totales_semanas_con_porcentaje[semana] = {
                "total": total,
                "promedio": total / 7,
                "porcentaje": round(porcentaje, 1),
            }

        return {
            "tabla": tabla,
            "semanas": semanas_ordenadas,
            "dias": dias_semana,
            "totales_semanas": totales_semanas_con_porcentaje,
            "totales_dias": totales_dias_con_porcentaje,
            "total_general": total_general,
            "promedio_diario": promedio_diario,
            "dias_registrados": dias_registrados,
        }

    @staticmethod
    def crear_tabla_mensual(ingresos):
        """
        Crea una tabla organizada por meses y semanas.

        Args:
            ingresos (QuerySet): Todos los registros de ingresos

        Returns:
            dict: Estructura de datos para la tabla mensual
        """
        if not ingresos.exists():
            return {"tabla": {}, "meses": [], "semanas": []}

        # Agrupar por mes y semana
        tabla = {}

        for ingreso in ingresos:
            mes_key = f"{ingreso.año}-{ingreso.mes:02d}"
            semana_key = ingreso.numero_semana

            if mes_key not in tabla:
                tabla[mes_key] = {}

            if semana_key not in tabla[mes_key]:
                tabla[mes_key][semana_key] = Decimal("0.00")

            tabla[mes_key][semana_key] += ingreso.monto

        # Obtener lista de meses y semanas únicas
        meses = sorted(tabla.keys())
        todas_semanas = set()
        for semanas in tabla.values():
            todas_semanas.update(semanas.keys())
        semanas_unicas = sorted(todas_semanas)

        return {"tabla": tabla, "meses": meses, "semanas": semanas_unicas}
