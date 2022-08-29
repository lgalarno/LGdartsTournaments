from django.contrib.auth.decorators import login_required
from django.urls import path

from games import views
from .views import TournamentListView, CreateTournament, TournamentDetailView, TournamentUpdateView, \
    TournamentDeleteView, AllTournamentsListView, GameUpdateView

app_name = 'games'

urlpatterns = [
    path('list-tournaments', TournamentListView.as_view(), name="list-tournaments"),
    path('list-all-tournaments', AllTournamentsListView.as_view(), name="list-all-tournaments"),
    path('create-tournaments/', CreateTournament.as_view(), name="create-tournaments"),
    path('tournament-detail/<int:pk>/', TournamentDetailView.as_view(), name="tournament-detail"),
    path('update-tournament/<int:pk>/', TournamentUpdateView.as_view(), name="update-tournament"),
    path('delete-tournament/<int:pk>/', TournamentDeleteView.as_view(), name="delete-tournament"),
    path('delete-game/<int:pk>/', views.delete_game, name="delete-game"),
    path('game-create/<int:tournament_id>/', views.game_create, name="game-create"),
    path('edit-game/<int:pk>/', GameUpdateView.as_view(), name="edit-game"),
]
