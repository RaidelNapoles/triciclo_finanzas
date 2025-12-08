from django.urls import path
from .views import dashboard_views

app_name = "finanzas_app"

urlpatterns = [
    path("", dashboard_views.index, name="dashboard"),
]
