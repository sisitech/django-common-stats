
from rest_framework import  generics
from stats.models import Export
from stats.exports.serializers import ExportSerializer
from rest_framework.permissions import IsAuthenticated
from mylib.my_common import MyDjangoFilterBackend, MyStandardPagination

class ListCreateExportsAPIView(generics.ListAPIView):
    serializer_class = ExportSerializer
    queryset = Export.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    pagination_class = MyStandardPagination


    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)


class RetrieveUpdateDestroyExportAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExportSerializer
    queryset = Export.objects.all()
    permission_classes = (IsAuthenticated,)
