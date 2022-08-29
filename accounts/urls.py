from django.urls import path

from accounts import views
from .views import EditProfile, CreateDarts, DartsDetailView, DartsUpdateView, DartsDeleteView, DartsListView, AllDartsListView

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('register/', views.register_view, name="register"),
    path('edit/', EditProfile.as_view(), name="EditProfile"),
    path('create-darts/', CreateDarts.as_view(), name="create-darts"),
    path('update-darts/<int:pk>/', DartsUpdateView.as_view(), name="update-darts"),
    path('darts-detail/<int:pk>/', DartsDetailView.as_view(), name="darts-detail"),
    path('delete-darts/<int:pk>/', DartsDeleteView.as_view(), name="delete-darts"),
    path('list-darts', DartsListView.as_view(), name="list-darts"),
    path('list-all-darts', AllDartsListView.as_view(), name="list-all-darts"),
]
