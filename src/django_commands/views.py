from django.conf import settings

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from .tasks import async_call_command


class CallCommandSerializer(Serializer):
    using = serializers.ChoiceField(
            choices=["thread", "local", "celery"],
            required=False, default="local")
    command = serializers.CharField()
    args = serializers.ListField(required=False, default=list)
    kwargs = serializers.DictField(required=False, default=dict)

    class Meta:
        fields = ["async", "command", "args", "kwargs"]


class CallCommandView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = CallCommandSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        command = data["command"]
        if command not in settings.DJANGO_COMMANDS_ALLOW_REMOTE_CALL:
            raise PermissionDenied(f"you are not allowed to call command `{command}`")
        if data["using"] == "celery":
            async_call_command.delay(
                    data["command"],
                    data["using"],
                    data["args"],
                    data["kwargs"],
            )
        else:
            async_call_command(
                    data["command"],
                    data["using"],
                    data["args"],
                    data["kwargs"],
            )
        return Response({})
