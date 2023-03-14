from rest_framework import status
from rest_framework.reverse import reverse
from core.tests import BaseAPITest
from stats.models import Export


class ExportTests(BaseAPITest):
    def create_export(self, status="Q", rows_count="1", exported_rows_count="1", type="C"):
        data = {"status": status, "rows_count": rows_count, "exported_rows_count": exported_rows_count, "type": type}
        return self.auth_client.post(reverse("list_create_exports"), data=data)

    def setUp(self):
        super(ExportTests, self).setUp()
        Export.objects.create(type="C")
        # self.create_export()

    def test_creating_export(self):
        resp = self.create_export(type="C")
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_listing_export(self):
        resp = self.auth_client.get(reverse("list_create_exports"))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_retrieving_export(self):
        resp = self.auth_client.get(reverse("retrieve_update_destroy_export", kwargs={"pk": 1}))
        # print(resp.json())
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["type"], "C")

    def test_updating_export(self):
        resp = self.auth_client.patch(reverse("retrieve_update_destroy_export", kwargs={"pk": 1}), data={"name": "madC"})
        self.assertEquals(resp.status_code, status.HTTP_200_OK)
        self.assertEquals(resp.data["name"], "madC")
