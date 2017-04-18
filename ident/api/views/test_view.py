from rest_framework import views
from rest_framework.response import Response
from api.services import test_service

class TestView(views.APIView):
    def get(self, request):
        return Response(test_service.hello_world())
    def post(self, request):
        return Response(test_service.hello_world())
