from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet

from ...models import Entry
from .serializers import EntrySerializer


class ReadonlyTransactionViewset(ReadOnlyModelViewSet):
    pass

class ReadonlyAccountViewSet(ReadOnlyModelViewSet):
    pass
