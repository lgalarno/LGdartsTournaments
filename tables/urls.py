from django.contrib.auth.decorators import login_required
from django.urls import path

from tables import views
# from .views import

app_name = 'tables'

urlpatterns = [
    path('export-zip/<int:tournament_id>/', login_required(views.export_zip), name="export-zip"),
    path('download/<slug>/', login_required(views.downloadzip), name="download-zip"),
    path('delete-zip/<int:pk>/', login_required(views.deletezip), name="delete-zip"),
    path('export-csv/<int:tournament_id>/<tbl_type>/', login_required(views.export_csv), name="export-csv"),
    path('tournament-tables/<int:tournament_id>/<tbl_type>/', views.tournament_tables, name="tournament-tables"),
    path('tournament-rr-tables/<int:tournament_id>/', views.tournament_rr_tables, name="tournament-rr-tables")
]
