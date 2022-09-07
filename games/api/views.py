from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

import json

from games.models import Tournament


class CreateRoundRobinAPI(APIView):
    """
    * Requires authentication.
    """
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, tournament_id=None):
        obj = get_object_or_404(Tournament, pk=tournament_id)
        print(request.GET)
        nrounds = self.request.GET.get('nrounds', None)
        data = {
            'games': obj.name,
            'nrounds': nrounds
        }
        return Response(data)
