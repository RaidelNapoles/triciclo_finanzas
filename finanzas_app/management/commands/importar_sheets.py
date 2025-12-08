from django.core.management.base import BaseCommand
from django.utils import timezone
import pandas as pd
import datetime
from decimal import Decimal
import sys

from finanzas_app.models.ingresos import Recaudacion


class Command(BaseCommand):
    help = "Importa datos desde un archivo CSV/Excel exportado desde Google Sheets"

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=str, help="Ruta del archivo CSV o Excel")
        parser.add_argument(
            "--hoja",
            type=str,
            default=0,
            help="Nombre o índice de la hoja (para archivos Excel)",
        )
        parser.add_argument(
            "--sobreescribir",
            action="store_true",
            help="Sobreescribir registros existentes",
        )

    def handle(self, *args, **options):
        archivo = options["archivo"]
        hoja = options["hoja"]
        sobreescribir = options["sobreescribir"]

        self.stdout.write(self.style.SUCCESS(f"📥 Importando datos desde: {archivo}"))

        try:
            # Determinar tipo de archivo
            if archivo.endswith(".csv"):
                df = pd.read_csv(archivo, encoding="utf-8")
            elif archivo.endswith((".xls", ".xlsx")):
                df = pd.read_excel(archivo, sheet_name=hoja)
            else:
                self.stdout.write(self.style.ERROR("Formato de archivo no soportado"))
                return

            registros_importados = 0
            registros_actualizados = 0
            registros_omitidos = 0

            for index, row in df.iterrows():
                try:
                    # Buscar columnas
                    fecha_col = None
                    monto_col = None

                    # Buscar por nombres
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(term in col_lower for term in ["fecha", "date"]):
                            fecha_col = col
                        elif any(
                            term in col_lower
                            for term in ["monto", "cantidad", "recaud", "amount"]
                        ):
                            monto_col = col

                    # Usar primeras columnas si no se encontraron
                    if not fecha_col and len(df.columns) >= 1:
                        fecha_col = df.columns[0]
                    if not monto_col and len(df.columns) >= 2:
                        monto_col = df.columns[1]

                    # Obtener valores
                    fecha_val = row[fecha_col] if fecha_col else None
                    monto_val = row[monto_col] if monto_col else None

                    if pd.isna(fecha_val) or pd.isna(monto_val):
                        continue

                    # Parsear fecha
                    fecha = None

                    if hasattr(fecha_val, "date"):
                        fecha = fecha_val.date()
                    elif isinstance(fecha_val, str):
                        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]:
                            try:
                                fecha = datetime.datetime.strptime(
                                    str(fecha_val).strip(), fmt
                                ).date()
                                break
                            except:
                                continue

                    if not fecha:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Fila {index+1}: Fecha no válida: {fecha_val}"
                            )
                        )
                        continue

                    # Parsear monto
                    monto_str = str(monto_val).replace("$", "").replace(",", "").strip()
                    try:
                        monto = Decimal(monto_str)
                    except:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Fila {index+1}: Monto no válido: {monto_val}"
                            )
                        )
                        continue

                    # Verificar si ya existe
                    registro_existente = Recaudacion.objects.filter(fecha=fecha).first()

                    if registro_existente:
                        if sobreescribir:
                            registro_existente.monto = monto
                            registro_existente.save()
                            registros_actualizados += 1
                            self.stdout.write(
                                self.style.WARNING(f"↻ Actualizado: {fecha} - ${monto}")
                            )
                        else:
                            registros_omitidos += 1
                    else:
                        # Crear nuevo registro
                        registro = Recaudacion(fecha=fecha, monto=monto)
                        registro.save()
                        registros_importados += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Importado: {fecha} - ${monto}")
                        )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Fila {index+1}: Error - {str(e)}")
                    )

            # Resumen
            self.stdout.write(self.style.SUCCESS("\n" + "=" * 50))
            self.stdout.write(self.style.SUCCESS("📊 RESUMEN DE IMPORTACIÓN"))
            self.stdout.write(self.style.SUCCESS("=" * 50))
            self.stdout.write(
                self.style.SUCCESS(f"✅ Registros importados: {registros_importados}")
            )
            if sobreescribir:
                self.stdout.write(
                    self.style.WARNING(
                        f"↻ Registros actualizados: {registros_actualizados}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⏭️  Registros omitidos (duplicados): {registros_omitidos}"
                    )
                )

            total_actual = Recaudacion.objects.count()
            self.stdout.write(
                self.style.INFO(f"📋 Total en base de datos: {total_actual}")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al importar archivo: {str(e)}"))
