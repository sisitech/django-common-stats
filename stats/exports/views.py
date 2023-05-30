from rest_framework import generics
from stats.models import Export
from stats.exports.serializers import CustomExportSerializer, ExportSerializer
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


class ListCreateCustomExportsAPIView(generics.ListCreateAPIView):
    serializer_class = CustomExportSerializer
    queryset = Export.objects.all()
    filter_backends = (MyDjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    pagination_class = MyStandardPagination

    def perform_create(self, serializer):
        return serializer.save(
            is_custom=True,
            type="P",
            user_id=self.request.user.id,
        )

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id, is_custom=True)


class RetrieveUpdateDestroyExportAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExportSerializer
    queryset = Export.objects.all()
    permission_classes = (IsAuthenticated,)
