from django.urls import path

from .views import CreateRoundRobinAPI
app_name = 'games-api'


urlpatterns = [
    path('create-round-robin/<int:tournament_id>/', CreateRoundRobinAPI.as_view(), name='CreateRoundRobinAPI'),
]
