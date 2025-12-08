from finanzas_app.models.ingresos import Recaudacion


class EstadisticaService:
    @classmethod
    def obtener_estadisticas(cls):
        """Obtiene estadísticas generales de todos los registros"""
        registros = Recaudacion.objects.all()

        if not registros.exists():
            return {
                "total_recaudado": 0,
                "promedio_diario": 0,
                "dias_registrados": 0,
                "mejor_dia": None,
                "peor_dia": None,
            }

        total = sum(r.monto for r in registros)
        promedio = total / registros.count()

        mejor_dia = registros.order_by("-monto").first()
        peor_dia = registros.order_by("monto").first()

        return {
            "total_recaudado": total,
            "promedio_diario": promedio,
            "dias_registrados": registros.count(),
            "mejor_dia": mejor_dia,
            "peor_dia": peor_dia,
        }

    @classmethod
    def obtener_por_semana(cls):
        """Agrupa registros por semana"""
        registros = Recaudacion.objects.all().order_by("fecha")

        semanas = {}
        for registro in registros:
            semana_key = f"{registro.numero_semana}"
            if semana_key not in semanas:
                semanas[semana_key] = {
                    "semana": registro.numero_semana,
                    "total": 0,
                    "dias": 0,
                    "promedio": 0,
                }

            semanas[semana_key]["total"] += float(registro.monto)
            semanas[semana_key]["dias"] += 1

        # Calcular promedio por semana
        for semana in semanas.values():
            semana["promedio"] = semana["total"] / semana["dias"]

        return semanas

    @classmethod
    def obtener_por_mes(cls):
        """Agrupa registros por mes"""
        registros = Recaudacion.objects.all().order_by("fecha")

        meses = {}
        for registro in registros:
            registro_anno = registro.fecha.year
            registro_mes = registro.fecha.month
            mes_key = f"{registro_anno}-{registro_mes}"
            if mes_key not in meses:
                meses_nombres = [
                    "Enero",
                    "Febrero",
                    "Marzo",
                    "Abril",
                    "Mayo",
                    "Junio",
                    "Julio",
                    "Agosto",
                    "Septiembre",
                    "Octubre",
                    "Noviembre",
                    "Diciembre",
                ]
                meses[mes_key] = {
                    "mes": registro_mes,
                    "mes_nombre": meses_nombres[registro_mes - 1],
                    "año": registro_anno,
                    "total": 0,
                    "dias": 0,
                    "promedio": 0,
                }

            meses[mes_key]["total"] += float(registro.monto)
            meses[mes_key]["dias"] += 1

        # Calcular promedio por mes
        for mes in meses.values():
            mes["promedio"] = mes["total"] / mes["dias"]

        return meses

    @classmethod
    def obtener_por_dia_semana(cls):
        """Agrupa registros por día de la semana"""
        registros = Recaudacion.objects.all()

        dias_semana = {
            "Lunes": {"total": 0, "count": 0, "promedio": 0},
            "Martes": {"total": 0, "count": 0, "promedio": 0},
            "Miércoles": {"total": 0, "count": 0, "promedio": 0},
            "Jueves": {"total": 0, "count": 0, "promedio": 0},
            "Viernes": {"total": 0, "count": 0, "promedio": 0},
            "Sábado": {"total": 0, "count": 0, "promedio": 0},
            "Domingo": {"total": 0, "count": 0, "promedio": 0},
        }

        for registro in registros:
            dia = registro.dia_semana
            dias_semana[dia]["total"] += float(registro.monto)
            dias_semana[dia]["count"] += 1

        # Calcular promedio por día
        for dia in dias_semana.values():
            if dia["count"] > 0:
                dia["promedio"] = dia["total"] / dia["count"]

        return dias_semana
