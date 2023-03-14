import inspect
import traceback

from django.test import TestCase, tag

# Create your tests here.
from rest_framework.reverse import reverse
from client.models import MyUser
from mylib.my_common import MyCustomException
from mylib.queryset2excel import importExcelCsv
from core.tests import BaseAPITest


from school.models import STUDENTS_STATS_DEFINTIONS, Student
from attendance.models import ATTENDANCE_STATS_DEFINTIONS


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

    def get_student_stats(self, stat_type, export=False):
        url = reverse("list_dynamic_students_statistics", kwargs={"type": stat_type})
        print(stat_type)
        url = "{}?export={}".format(url, "true" if export else "false")
        return self.auth_client.get(url)

    def get_attendance_stats(self, stat_type, export=False):
        url = reverse("list_dynamic_attendances_statistics", kwargs={"type": stat_type})
        url = "{}?export={}".format(url, "true" if export else "false")
        return self.auth_client.get(url)

    @tag("atg2")
    def test_attendance_class_stat(self):
        resp = self.take_attendance(date="2019-09-04", present=[1, 2], absent=[])
        resp = self.take_attendance(date="2019-09-05", present=[], absent=[1, 2])
        resp = self.take_attendance(date="2019-09-06", present=[], absent=[2])
        resp = self.get_attendance_stats("class", False)
        print(resp.json())

    @tag("tg2")
    def test_students_class_stat(self):

        resp = self.get_student_stats("class", False)
        # print(resp.json())
        data = resp.json()
        self.assertEquals(resp.status_code, 200)
        results = data["results"]
        self.assertEquals(data["count"], 2)
        self.assertEquals(results[1]["class_name"], "7")

    @tag("tg")
    def test_students_school_stat(self):
        resp = self.get_student_stats("school", False)
        # print(resp.json())
        data = resp.json()
        self.assertEquals(resp.status_code, 200)
        results = data["results"]
        self.assertEquals(data["count"], 2)
        user = MyUser.objects.get(username="PADD")
        self.set_authenticated_user(user.id)
        resp = self.get_student_stats("school", False)
        # print(resp.json())
        self.assertEquals(resp.json()["count"], 1)
        # print(resp.json())


ignored_stats = ["day", "age"]
# Include all the defined endpoints tests
function_prefix_name = "test_students_stats_"


def fun_test(self):
    fun_name = self.__str__().split(" ")[0]
    stat_type = fun_name.split(function_prefix_name)[1]
    # print()
    resp = self.get_student_stats(stat_type)
    # print(resp.json())
    self.assertEquals(resp.status_code, 200)

    resp = self.get_student_stats(stat_type, export=True)
    self.assertEquals(resp.status_code, 201)
    self.assertEquals(resp.json()["status"], "Queued")


for stat_type in STUDENTS_STATS_DEFINTIONS:
    if stat_type in ignored_stats:
        continue
    # print(stat_type)
    setattr(
        StatsTests,
        "{}{}".format(function_prefix_name, stat_type),
        fun_test,
    )

attendance_function_prefix_name = "test_attendance_stats_"


def fun_test_attendance(self):
    fun_name = self.__str__().split(" ")[0]
    stat_type = fun_name.split(attendance_function_prefix_name)[1]
    resp = self.get_attendance_stats(stat_type)
    # print(resp.json())
    self.assertEquals(resp.status_code, 200)

    resp = self.get_attendance_stats(stat_type, export=True)
    self.assertEquals(resp.status_code, 201)
    self.assertEquals(resp.json()["status"], "Queued")


for stat_type in ATTENDANCE_STATS_DEFINTIONS:
    if stat_type in ignored_stats:
        continue

    setattr(
        StatsTests,
        "{}{}".format(attendance_function_prefix_name, stat_type),
        fun_test_attendance,
    )
