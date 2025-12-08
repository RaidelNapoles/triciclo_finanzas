# ingresos/graficos.py
"""
Módulo para generar gráficos profesionales con Matplotlib.
Configuración optimizada para visualización web con etiquetas claras.
"""

import matplotlib.pyplot as plt
import matplotlib
from django.conf import settings
import io
import base64
import copy
import numpy as np
from decimal import Decimal

# Configurar Matplotlib para modo no interactivo
matplotlib.use("Agg")

# Configuración global de estilos
plt.style.use("seaborn-v0_8-whitegrid")  # Estilo profesional con grid

# Configuración personalizada para gráficos optimizados
CONFIG_GRAFICOS = {
    # Tamaños optimizados para visualización web
    "tamano_figura": (14, 8),  # Más ancho para mejor visualización
    "dpi": 120,  # Alta resolución
    "colores": {
        "principal": "#3498db",  # Azul principal
        "secundario": "#2ecc71",  # Verde éxito
        "acento": "#e74c3c",  # Rojo para atención
        "neutro": "#95a5a6",  # Gris neutro
        "destacado": "#f39c12",  # Naranja para fines de semana
        "fondo": "#ffffff",  # Blanco puro
        "grid": "#ecf0f1",  # Grid muy suave
        "texto": "#2c3e50",  # Texto oscuro
    },
    # Configuración de fuentes
    "fuentes": {
        "titulo": {"size": 18, "weight": "bold", "color": "#2c3e50"},
        "ejes": {"size": 14, "weight": "bold", "color": "#2c3e50"},
        "etiquetas": {"size": 12, "weight": "normal", "color": "#2c3e50"},
        "numeros": {"size": 11, "weight": "bold", "color": "#2c3e50"},
        "leyenda": {"size": 12, "weight": "normal", "color": "#2c3e50"},
    },
    # Configuración de barras
    "barras": {
        "ancho": 0.7,
        "espaciado": 0.8,
        "borde_ancho": 1.5,
        "borde_color": "#ffffff",
        "transparencia": 0.85,
    },
    # Configuración de líneas
    "lineas": {
        "ancho": 3,
        "marcador_tamano": 10,
        "marcador_color": "#ffffff",
        "marcador_borde": 2,
    },
}


class GeneradorGraficos:
    """
    Clase para generar gráficos profesionales con etiquetas claras.

    Características:
    - Gráficos grandes y legibles
    - Etiquetas en cada barra con valores
    - Fuentes optimizadas para visualización web
    - Colores profesionales y consistentes
    - Layout responsivo
    """

    @staticmethod
    def crear_grafico_semanal(datos_semanales, max_semanas=30):
        """
        Crea gráfico de barras para ingresos semanales.

        Args:
            datos_semanales (list): Lista de diccionarios con datos semanales
            max_semanas (int): Máximo número de semanas a mostrar

        Returns:
            str: Imagen en base64
        """
        if not datos_semanales:
            return None

        # Limitar semanas para mejor visualización
        datos_a_mostrar = (
            datos_semanales[-max_semanas:]
            if len(datos_semanales) > max_semanas
            else datos_semanales
        )

        # Preparar datos
        semanas = []
        ingresos = []

        for semana in datos_a_mostrar:
            # Formato de etiqueta: Año-Semana
            etiqueta = f"Sem {semana['semana']}"
            if "año" in semana:
                etiqueta = f"{semana['año']}-{semana['semana']:02d}"
            semanas.append(etiqueta)
            ingresos.append(float(semana["total"]))

        # Crear figura con tamaño optimizado
        fig, ax = plt.subplots(
            figsize=CONFIG_GRAFICOS["tamano_figura"],
            dpi=CONFIG_GRAFICOS["dpi"],
            facecolor=CONFIG_GRAFICOS["colores"]["fondo"],
        )

        # Crear barras
        barras = ax.bar(
            semanas,
            ingresos,
            width=CONFIG_GRAFICOS["barras"]["ancho"],
            color=CONFIG_GRAFICOS["colores"]["principal"],
            edgecolor=CONFIG_GRAFICOS["barras"]["borde_color"],
            linewidth=CONFIG_GRAFICOS["barras"]["borde_ancho"],
            alpha=CONFIG_GRAFICOS["barras"]["transparencia"],
            zorder=3,
        )

        # AÑADIR ETIQUETAS EN CADA BARRA (MEJORA PRINCIPAL)
        GeneradorGraficos._agregar_etiquetas_barras(ax, barras)

        # Configurar título
        ax.set_title(
            "📊 INGRESOS SEMANALES",
            fontdict=CONFIG_GRAFICOS["fuentes"]["titulo"],
            pad=25,
        )

        # Configurar eje X
        ax.set_xlabel(
            "SEMANA", fontdict=CONFIG_GRAFICOS["fuentes"]["ejes"], labelpad=20
        )

        # Configurar eje Y
        ax.set_ylabel(
            "INGRESOS (CUP)", fontdict=CONFIG_GRAFICOS["fuentes"]["ejes"], labelpad=20
        )

        # Configurar ticks
        ax.tick_params(
            axis="both",
            labelsize=CONFIG_GRAFICOS["fuentes"]["etiquetas"]["size"],
            colors=CONFIG_GRAFICOS["fuentes"]["etiquetas"]["color"],
        )

        # Rotar etiquetas del eje X para mejor legibilidad
        plt.xticks(rotation=45, ha="right", rotation_mode="anchor")

        # Añadir grid profesional
        ax.grid(
            True,
            axis="y",
            alpha=0.3,
            color=CONFIG_GRAFICOS["colores"]["grid"],
            linestyle="--",
            linewidth=0.8,
            zorder=0,
        )

        # Remover bordes innecesarios
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_linewidth(0.5)
        ax.spines["bottom"].set_linewidth(0.5)

        # Añadir línea de promedio
        if ingresos:
            promedio = np.mean(ingresos)
            ax.axhline(
                y=promedio,
                color=CONFIG_GRAFICOS["colores"]["acento"],
                linestyle="--",
                linewidth=2,
                alpha=0.7,
                label=f"Promedio: ${promedio:,.2f}",
            )

            # Añadir leyenda
            ax.legend(
                fontsize=CONFIG_GRAFICOS["fuentes"]["leyenda"]["size"],
                loc="upper right",
                framealpha=0.9,
                fancybox=True,
                shadow=True,
            )

        # Ajustar layout automáticamente
        plt.tight_layout()

        # Convertir a base64
        imagen = GeneradorGraficos._figura_a_base64(fig)
        plt.close(fig)

        return imagen

    @staticmethod
    def crear_grafico_diario(datos_diarios):
        """
        Crea gráfico de barras para recaudación por día de la semana.

        Args:
            datos_diarios (list): Lista de recaudaciones por día

        Returns:
            str: Imagen en base64
        """
        if not datos_diarios:
            return None

        # Ordenar por día de la semana
        dias_orden = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]

        # Preparar datos ordenados
        dias = []
        recaudacion = []

        for nombre_dia in dias_orden:
            datos_dia = datos_diarios[nombre_dia]
            dias.append(nombre_dia[:3])  # Abreviar a 3 letras
            recaudacion.append(float(datos_dia["total"]))

        # Crear figura
        fig, ax = plt.subplots(
            figsize=CONFIG_GRAFICOS["tamano_figura"],
            dpi=CONFIG_GRAFICOS["dpi"],
            facecolor=CONFIG_GRAFICOS["colores"]["fondo"],
        )

        # Crear barras con colores diferenciados
        colores = []
        for dia in dias:
            if dia in ["Sáb", "Dom"]:
                colores.append(CONFIG_GRAFICOS["colores"]["destacado"])
            else:
                colores.append(CONFIG_GRAFICOS["colores"]["secundario"])

        barras = ax.bar(
            dias,
            recaudacion,
            width=CONFIG_GRAFICOS["barras"]["ancho"],
            color=colores,
            edgecolor=CONFIG_GRAFICOS["barras"]["borde_color"],
            linewidth=CONFIG_GRAFICOS["barras"]["borde_ancho"],
            alpha=CONFIG_GRAFICOS["barras"]["transparencia"],
            zorder=3,
        )

        font_config = copy.deepcopy(CONFIG_GRAFICOS["fuentes"])
        font_config["titulo"]["size"] = 30
        font_config["ejes"]["size"] = 20
        font_config["etiquetas"]["size"] = 20
        font_config["numeros"]["size"] = 27
        font_config["leyenda"]["size"] = 25

        # AÑADIR ETIQUETAS EN CADA BARRA
        GeneradorGraficos._agregar_etiquetas_barras(ax, barras, font_size=20)

        # Configurar título
        ax.set_title(
            "📈 INGRESOS POR DÍA",
            fontdict=font_config["titulo"],
            pad=25,
        )

        # Configurar eje X
        ax.set_xlabel("DÍA DE LA SEMANA", fontdict=font_config["ejes"], labelpad=20)

        # Configurar eje Y
        ax.set_ylabel(
            "TOTAL DE INGRESOS (CUP)",
            fontdict=font_config["ejes"],
            labelpad=20,
        )

        # Configurar ticks
        ax.tick_params(
            axis="both",
            labelsize=font_config["etiquetas"]["size"],
            colors=font_config["etiquetas"]["color"],
        )

        # Añadir grid
        ax.grid(
            True,
            axis="y",
            alpha=0.3,
            color=CONFIG_GRAFICOS["colores"]["grid"],
            linestyle="--",
            linewidth=0.8,
            zorder=0,
        )

        # Remover bordes
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Crear leyenda personalizada
        from matplotlib.patches import Patch

        elementos_leyenda = [
            Patch(
                facecolor=CONFIG_GRAFICOS["colores"]["secundario"],
                label="Días Laborables",
                alpha=CONFIG_GRAFICOS["barras"]["transparencia"],
            ),
            Patch(
                facecolor=CONFIG_GRAFICOS["colores"]["destacado"],
                label="Fin de Semana",
                alpha=CONFIG_GRAFICOS["barras"]["transparencia"],
            ),
        ]

        # ax.legend(
        #     handles=elementos_leyenda,
        #     fontsize=CONFIG_GRAFICOS["fuentes"]["leyenda"]["size"],
        #     loc="upper right",
        #     framealpha=0.9,
        # )

        # Ajustar layout
        plt.tight_layout()

        # Convertir a base64
        imagen = GeneradorGraficos._figura_a_base64(fig)
        plt.close(fig)

        return imagen

    @staticmethod
    def crear_grafico_promedio_diario(promedios_diarios):
        """
        Crea gráfico de barras para promedios diarios.

        Args:
            promedios_diarios (list): Lista de promedios por día

        Returns:
            str: Imagen en base64
        """
        if not promedios_diarios:
            return None

        # Ordenar por día de la semana
        dias_orden = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]

        # Preparar datos ordenados
        dias = []
        promedios = []

        for nombre_dia in dias_orden:
            datos_dia = promedios_diarios[nombre_dia]
            dias.append(nombre_dia[:3])  # Abreviar a 3 letras
            promedios.append(float(datos_dia["promedio"]))

        # Crear figura
        fig, ax = plt.subplots(
            figsize=CONFIG_GRAFICOS["tamano_figura"],
            dpi=CONFIG_GRAFICOS["dpi"],
            facecolor=CONFIG_GRAFICOS["colores"]["fondo"],
        )

        # Crear barras con colores diferenciados
        colores = []
        for dia in dias:
            if dia in ["Sáb", "Dom"]:
                colores.append(CONFIG_GRAFICOS["colores"]["destacado"])
            else:
                colores.append(CONFIG_GRAFICOS["colores"]["secundario"])

        barras = ax.bar(
            dias,
            promedios,
            width=CONFIG_GRAFICOS["barras"]["ancho"],
            color=colores,
            edgecolor=CONFIG_GRAFICOS["barras"]["borde_color"],
            linewidth=CONFIG_GRAFICOS["barras"]["borde_ancho"],
            alpha=CONFIG_GRAFICOS["barras"]["transparencia"],
            zorder=3,
        )

        font_config = copy.deepcopy(CONFIG_GRAFICOS["fuentes"])
        font_config["titulo"]["size"] = 30
        font_config["ejes"]["size"] = 20
        font_config["etiquetas"]["size"] = 20
        font_config["numeros"]["size"] = 27
        font_config["leyenda"]["size"] = 25

        # AÑADIR ETIQUETAS EN CADA BARRA
        GeneradorGraficos._agregar_etiquetas_barras(ax, barras, font_size=20)

        # Configurar título
        ax.set_title(
            "📈 PROMEDIO DE INGRESOS POR DÍA",
            fontdict=font_config["titulo"],
            pad=25,
        )

        # Configurar eje X
        ax.set_xlabel("DÍA DE LA SEMANA", fontdict=font_config["ejes"], labelpad=20)

        # Configurar eje Y
        ax.set_ylabel(
            "PROMEDIO DE INGRESOS (CUP)",
            fontdict=font_config["ejes"],
            labelpad=20,
        )

        # Configurar ticks
        ax.tick_params(
            axis="both",
            labelsize=font_config["etiquetas"]["size"],
            colors=font_config["etiquetas"]["color"],
        )

        # Añadir grid
        ax.grid(
            True,
            axis="y",
            alpha=0.3,
            color=CONFIG_GRAFICOS["colores"]["grid"],
            linestyle="--",
            linewidth=0.8,
            zorder=0,
        )

        # Remover bordes
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Crear leyenda personalizada
        from matplotlib.patches import Patch

        elementos_leyenda = [
            Patch(
                facecolor=CONFIG_GRAFICOS["colores"]["secundario"],
                label="Días Laborables",
                alpha=CONFIG_GRAFICOS["barras"]["transparencia"],
            ),
            Patch(
                facecolor=CONFIG_GRAFICOS["colores"]["destacado"],
                label="Fin de Semana",
                alpha=CONFIG_GRAFICOS["barras"]["transparencia"],
            ),
        ]

        # ax.legend(
        #     handles=elementos_leyenda,
        #     fontsize=CONFIG_GRAFICOS["fuentes"]["leyenda"]["size"],
        #     loc="upper right",
        #     framealpha=0.9,
        # )

        # Ajustar layout
        plt.tight_layout()

        # Convertir a base64
        imagen = GeneradorGraficos._figura_a_base64(fig)
        plt.close(fig)

        return imagen

    @staticmethod
    def crear_grafico_mensual(datos_mensuales, max_meses=12):
        """
        Crea gráfico de línea para tendencia mensual.

        Args:
            datos_mensuales (list): Datos mensuales
            max_meses (int): Máximo de meses a mostrar

        Returns:
            str: Imagen en base64
        """
        if not datos_mensuales:
            return None

        # Limitar meses para mejor visualización
        datos_a_mostrar = (
            datos_mensuales[-max_meses:]
            if len(datos_mensuales) > max_meses
            else datos_mensuales
        )

        # Preparar datos
        meses = []
        ingresos = []

        for datos_mes in datos_a_mostrar:
            etiqueta = f"{datos_mes['año']}-{datos_mes['mes']:02d}"
            meses.append(etiqueta)
            ingresos.append(float(datos_mes["total"]))

        # Crear figura
        fig, ax = plt.subplots(
            figsize=CONFIG_GRAFICOS["tamano_figura"],
            dpi=CONFIG_GRAFICOS["dpi"],
            facecolor=CONFIG_GRAFICOS["colores"]["fondo"],
        )

        # Crear línea con marcadores
        linea = ax.plot(
            meses,
            ingresos,
            marker="o",
            markersize=CONFIG_GRAFICOS["lineas"]["marcador_tamano"],
            markerfacecolor=CONFIG_GRAFICOS["lineas"]["marcador_color"],
            markeredgecolor=CONFIG_GRAFICOS["colores"]["principal"],
            markeredgewidth=CONFIG_GRAFICOS["lineas"]["marcador_borde"],
            linewidth=CONFIG_GRAFICOS["lineas"]["ancho"],
            color=CONFIG_GRAFICOS["colores"]["principal"],
            alpha=0.9,
            zorder=3,
            label="Ingresos Mensuales",
        )[0]

        # AÑADIR ETIQUETAS EN CADA PUNTO
        GeneradorGraficos._agregar_etiquetas_puntos(ax, meses, ingresos)

        # Configurar título
        ax.set_title(
            "📈 TENDENCIA DE INGRESOS MENSUALES",
            fontdict=CONFIG_GRAFICOS["fuentes"]["titulo"],
            pad=25,
        )

        # Configurar eje X
        ax.set_xlabel("MES", fontdict=CONFIG_GRAFICOS["fuentes"]["ejes"], labelpad=20)

        # Configurar eje Y
        ax.set_ylabel(
            "INGRESOS (CUP)", fontdict=CONFIG_GRAFICOS["fuentes"]["ejes"], labelpad=20
        )

        # Configurar ticks
        ax.tick_params(
            axis="both",
            labelsize=CONFIG_GRAFICOS["fuentes"]["etiquetas"]["size"],
            colors=CONFIG_GRAFICOS["fuentes"]["etiquetas"]["color"],
        )

        # Rotar etiquetas del eje X
        plt.xticks(rotation=45, ha="right", rotation_mode="anchor")

        # Añadir grid
        ax.grid(
            True,
            alpha=0.3,
            color=CONFIG_GRAFICOS["colores"]["grid"],
            linestyle="--",
            linewidth=0.8,
            zorder=0,
        )

        # Remover bordes
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Añadir área sombreada bajo la línea
        ax.fill_between(
            meses,
            ingresos,
            alpha=0.2,
            color=CONFIG_GRAFICOS["colores"]["principal"],
            zorder=1,
        )

        # Añadir leyenda
        ax.legend(
            fontsize=CONFIG_GRAFICOS["fuentes"]["leyenda"]["size"],
            loc="upper left",
            framealpha=0.9,
        )

        # Ajustar layout
        plt.tight_layout()

        # Convertir a base64
        imagen = GeneradorGraficos._figura_a_base64(fig)
        plt.close(fig)

        return imagen

    @staticmethod
    def crear_grafico_comparativo(
        datos_actuales, datos_anteriores, titulo="COMPARACIÓN"
    ):
        """
        Crea gráfico de comparación entre dos conjuntos de datos.

        Args:
            datos_actuales: Datos actuales
            datos_anteriores: Datos anteriores
            titulo: Título del gráfico

        Returns:
            str: Imagen en base64
        """
        # Preparar datos
        etiquetas = ["Actual", "Anterior"]
        valores = [
            float(datos_actuales[0]["total_ingresos"]) if datos_actuales else 0,
            float(datos_anteriores[0]["total_ingresos"]) if datos_anteriores else 0,
        ]

        # Crear figura
        fig, ax = plt.subplots(
            figsize=(12, 7),
            dpi=CONFIG_GRAFICOS["dpi"],
            facecolor=CONFIG_GRAFICOS["colores"]["fondo"],
        )

        # Crear barras
        colores = [
            CONFIG_GRAFICOS["colores"]["principal"],
            CONFIG_GRAFICOS["colores"]["neutro"],
        ]

        barras = ax.bar(
            etiquetas,
            valores,
            width=0.6,
            color=colores,
            edgecolor=CONFIG_GRAFICOS["barras"]["borde_color"],
            linewidth=CONFIG_GRAFICOS["barras"]["borde_ancho"],
            alpha=CONFIG_GRAFICOS["barras"]["transparencia"],
            zorder=3,
        )

        # AÑADIR ETIQUETAS EN CADA BARRA
        GeneradorGraficos._agregar_etiquetas_barras(ax, barras)

        # Configurar título
        ax.set_title(titulo, fontdict=CONFIG_GRAFICOS["fuentes"]["titulo"], pad=25)

        # Configurar eje Y
        ax.set_ylabel(
            "INGRESOS ($)", fontdict=CONFIG_GRAFICOS["fuentes"]["ejes"], labelpad=20
        )

        # Configurar ticks
        ax.tick_params(
            axis="both",
            labelsize=CONFIG_GRAFICOS["fuentes"]["etiquetas"]["size"],
            colors=CONFIG_GRAFICOS["fuentes"]["etiquetas"]["color"],
        )

        # Remover bordes
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_visible(False)

        # Añadir grid
        ax.grid(
            True,
            axis="y",
            alpha=0.3,
            color=CONFIG_GRAFICOS["colores"]["grid"],
            linestyle="--",
            linewidth=0.8,
            zorder=0,
        )

        # Ajustar layout
        plt.tight_layout()

        # Convertir a base64
        imagen = GeneradorGraficos._figura_a_base64(fig)
        plt.close(fig)

        return imagen

    @staticmethod
    def _agregar_etiquetas_barras(ax, barras, font_size=12):
        """
        Agrega etiquetas de valor encima de cada barra.

        Args:
            ax: Ejes de Matplotlib
            barras: Objetos de barras
        """
        for barra in barras:
            altura = barra.get_height()
            if altura > 0:  # Solo mostrar etiquetas para valores positivos
                # Formatear valor con separadores de miles
                texto = f"${altura:,.0f}"

                # Calcular posición
                x_pos = barra.get_x() + barra.get_width() / 2
                y_pos = altura

                # Crear etiqueta
                ax.annotate(
                    texto,
                    xy=(x_pos, y_pos),
                    xytext=(0, 8),  # Desplazamiento vertical
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=font_size,
                    fontweight=CONFIG_GRAFICOS["fuentes"]["numeros"]["weight"],
                    color=CONFIG_GRAFICOS["fuentes"]["numeros"]["color"],
                    bbox=dict(
                        boxstyle="round,pad=0.3",
                        facecolor="white",
                        edgecolor=CONFIG_GRAFICOS["colores"]["grid"],
                        alpha=0.9,
                        linewidth=1,
                    ),
                )

    @staticmethod
    def _agregar_etiquetas_puntos(ax, x_valores, y_valores):
        """
        Agrega etiquetas de valor a los puntos de un gráfico de línea.

        Args:
            ax: Ejes de Matplotlib
            x_valores: Valores en el eje X
            y_valores: Valores en el eje Y
        """
        for i, (x, y) in enumerate(zip(x_valores, y_valores)):
            if y > 0:  # Solo mostrar etiquetas para valores positivos
                texto = f"${y:,.0f}"

                ax.annotate(
                    texto,
                    xy=(i, y),
                    xytext=(0, 12),  # Desplazamiento vertical
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=CONFIG_GRAFICOS["fuentes"]["numeros"]["size"] - 1,
                    fontweight=CONFIG_GRAFICOS["fuentes"]["numeros"]["weight"],
                    color=CONFIG_GRAFICOS["fuentes"]["numeros"]["color"],
                    bbox=dict(
                        boxstyle="round,pad=0.2",
                        facecolor="white",
                        edgecolor=CONFIG_GRAFICOS["colores"]["grid"],
                        alpha=0.9,
                        linewidth=1,
                    ),
                )

    @staticmethod
    def _figura_a_base64(fig):
        """
        Convierte una figura de Matplotlib a string base64.

        Args:
            fig: Figura de Matplotlib

        Returns:
            str: Imagen en formato base64
        """
        # Crear buffer
        buf = io.BytesIO()

        # Guardar figura con configuración optimizada
        fig.savefig(
            buf,
            format="png",
            dpi=CONFIG_GRAFICOS["dpi"],
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
            edgecolor="none",
            pad_inches=0.1,
        )
        buf.seek(0)

        # Codificar a base64
        imagen_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()

        return imagen_base64

    @staticmethod
    def obtener_todos_los_graficos(
        datos_semanales=None, promedios_diarios=None, datos_mensuales=None
    ):
        """
        Genera todos los gráficos disponibles.

        Args:
            datos_semanales: Datos semanales
            promedios_diarios: Promedios diarios
            datos_mensuales: Datos mensuales

        Returns:
            dict: Diccionario con todos los gráficos generados
        """
        graficos = {}

        # Gráfico semanal
        if datos_semanales:
            graficos["semanal"] = GeneradorGraficos.crear_grafico_semanal(
                datos_semanales
            )

        # Gráfico diario
        if promedios_diarios:
            graficos["diario"] = GeneradorGraficos.crear_grafico_diario(
                promedios_diarios
            )

        # Gráfico mensual
        if datos_mensuales:
            graficos["mensual"] = GeneradorGraficos.crear_grafico_mensual(
                datos_mensuales
            )

        return graficos
