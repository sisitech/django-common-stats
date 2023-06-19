from django.test import TestCase, tag

# Create your tests here.
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model

MyUser = get_user_model()
from mylib.my_common import MyCustomException
from mylib.queryset2excel import importExcelCsv
from core.tests import BaseAPITest


class StatsTests(BaseAPITest):
    def setUp(self):
        super(StatsTests, self).setUp()
        # self.create_export()

    @tag("csv")
    def test_opening_of_csv_fileReader(self):
        # filePath="/Users/micha/Downloads/Export Students by Class-46.xlsx"
        filePath = "/Users/micha/Downloads/Export Students by Id-45.xlsx"
        # filePath="/Users/micha/Downloads/Export Students by Id-10.xlsx"
        # for row in importExcelCsv(filePath,headers_only=True,include_rows_count=False):
        #     print(row)
        #
        # print("done ")
        # pass
