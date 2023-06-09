from django.conf.urls import url
from stats.exports.views import ListCreateCustomExportsAPIView, ListCreateExportsAPIView, RetrieveUpdateDestroyExportAPIView

urlpatterns = [
    url(r"^$", ListCreateExportsAPIView.as_view(), name="list_create_exports"),
    url(r"^custom/?$", ListCreateCustomExportsAPIView.as_view(), name="list_create_custom_exports"),
    url(r"^(?P<pk>[0-9]+)/?$", RetrieveUpdateDestroyExportAPIView.as_view(), name="retrieve_update_destroy_export"),
]
