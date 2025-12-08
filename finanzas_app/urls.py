from django.urls import path
from .views import dashboard_views, tabla_views

app_name = "finanzas_app"

urlpatterns = [
    path("", dashboard_views.index, name="dashboard"),
    path("listado/", tabla_views.tabla_semanal, name="listado_tabla"),
]
