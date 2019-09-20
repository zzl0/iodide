import json

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from server.notebooks.models import Notebook

from . import backends
from .exceptions import ParametersParseError
from .models import RemoteOperation
from .serializers import RemoteOperationSerializer


class RemoteOperationViewSet(viewsets.ModelViewSet):
    serializer_class = RemoteOperationSerializer
    http_method_names = ["post"]
    queryset = RemoteOperation.objects.all()

    def create(self, request):
        """
        This view received data as POST when the remote chunk is evaluated
        in the notebook.

        It creates RemoteOperation objects that contain all the needed
        information about remote operation from start to finish.
        """
        metadata = json.loads(self.request.data["metadata"])
        notebook = get_object_or_404(Notebook, id=metadata["notebook_id"])
        if notebook.owner != request.user:
            raise PermissionDenied

        # get the remote kernel slug and see if we have a matching backend
        backend = backends.get_backend(metadata["backend"], PermissionDenied)

        # parse the content provided from the client using the backend
        content = request.data["content"]
        try:
            parsed = backend.parse_chunk(content)
        except ParametersParseError:
            # TODO: do something smart here like letting users
            # know that the remote chunk can't be validated
            raise ValueError(
                "The remote chunk couldn't be parsed, please check the syntax and evaluate again."
            )

        operation = backend.create_operation(
            notebook,
            backend=backend,
            snippet=parsed["snippet"],
            filename=parsed["filename"],
            parameters=parsed["parameters"],
        )
        return Response(RemoteOperationSerializer(operation).data, status=status.HTTP_201_CREATED)