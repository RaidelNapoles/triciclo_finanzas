from django.urls import path
from .views import dashboard_views, tabla_views, deuda_views

app_name = "finanzas_app"

urlpatterns = [
    path("", dashboard_views.index, name="dashboard"),
    path("listado/", tabla_views.tabla_semanal, name="listado_tabla"),
    path("deuda-semanal/", deuda_views.deuda_semanal, name="deuda_semanal"),
]
