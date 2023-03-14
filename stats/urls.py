from django.conf.urls import url

from stats.views import OptimizedExportTriggerAPIView


urlpatterns = [
    url(r'^$', OptimizedExportTriggerAPIView.as_view(), name="trigger_export"),
# url(r'^attendances/(?P<type>.+)/?$', ListAttendanceDynamicStatisticsAPIView.as_view(),
#         name="list_dynamic_attendances_statistics"),
#     url(r'^students/(?P<type>.+)/?$', ListStudentsDynamicsAPIView.as_view(),
#         name="list_dynamic_students_statistics"),
]
